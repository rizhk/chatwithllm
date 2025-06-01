import {
  appendClientMessage,
  appendResponseMessages,
  createDataStream,
  smoothStream,
  streamText,
} from 'ai';

// export const runtime = 'edge';

type JSONValue =
  | null
  | string
  | number
  | boolean
  | { [key: string]: JSONValue }
  | Array<JSONValue>;

interface DataStreamPart<CODE extends string, NAME extends string, TYPE> {
  code: CODE;
  name: NAME;
  parse: (value: JSONValue) => {
    type: NAME;
    value: TYPE;
  };
}


interface LanguageModelV1Source {
  readonly toolName?: string;
}

type ToolCall<NAME extends string, ARGS> = {
  toolName: NAME;
  args: ARGS;
  argsText: string;
  state: 'partial-call' | 'call';
};

type ToolResult<NAME extends string, ARGS, RESPONSE> = {
  toolName: NAME;
  args: ARGS;
  response: RESPONSE;
};

declare const dataStreamParts: readonly [
  DataStreamPart<"0", "text", string>,
  DataStreamPart<"2", "data", JSONValue[]>,
  DataStreamPart<"3", "error", string>,
  DataStreamPart<"8", "message_annotations", JSONValue[]>,
  DataStreamPart<"9", "tool_call", ToolCall<string, any>>,
  DataStreamPart<"a", "tool_result", Omit<ToolResult<string, any, any>, "args" | "toolName">>,
  DataStreamPart<"b", "tool_call_streaming_start", { toolCallId: string; toolName: string }>,
  DataStreamPart<"c", "tool_call_delta", { toolCallId: string; argsTextDelta: string }>,
  DataStreamPart<"d", "finish_message", { finishReason: string; usage?: { promptTokens: number; completionTokens: number } }>,
  DataStreamPart<"e", "finish_step", { isContinued: boolean; finishReason: string; usage?: { promptTokens: number; completionTokens: number } }>,
  DataStreamPart<"f", "start_step", { messageId: string }>,
  DataStreamPart<"g", "reasoning", string>,
  DataStreamPart<"h", "source", LanguageModelV1Source>,
  DataStreamPart<"i", "redacted_reasoning", { data: string }>,
  DataStreamPart<"j", "reasoning_signature", { signature: string }>,
  DataStreamPart<"k", "file", { data: string; mimeType: string }>
];

type DataStreamParts = (typeof dataStreamParts)[number];


declare const DataStreamStringPrefixes: {
  readonly text: "0";
  readonly data: "2";
  readonly error: "3";
  readonly message_annotations: "8";
  readonly tool_call: "9";
  readonly tool_result: "a";
  readonly tool_call_streaming_start: "b";
  readonly tool_call_delta: "c";
  readonly finish_message: "d";
  readonly finish_step: "e";
  readonly start_step: "f";
  readonly reasoning: "g";
  readonly source: "h";
  readonly redacted_reasoning: "i";
  readonly reasoning_signature: "j";
  readonly file: "k";
};

type DataStreamString = `${(typeof DataStreamStringPrefixes)[keyof typeof DataStreamStringPrefixes]}:${string}`;


import { auth, type UserType } from '@/app/(auth)/auth';
import { type RequestHints, systemPrompt } from '@/lib/ai/prompts';
import {
  createStreamId,
  deleteChatById,
  getChatById,
  getMessageCountByUserId,
  getMessagesByChatId,
  getStreamIdsByChatId,
  saveChat,
  saveMessages,
} from '@/lib/db/queries';
import { generateUUID, getTrailingMessageId } from '@/lib/utils';
import { generateTitleFromUserMessage } from '../../actions';
import { createDocument } from '@/lib/ai/tools/create-document';
import { updateDocument } from '@/lib/ai/tools/update-document';
import { requestSuggestions } from '@/lib/ai/tools/request-suggestions';
import { getWeather } from '@/lib/ai/tools/get-weather';
import { isProductionEnvironment } from '@/lib/constants';
import { myProvider } from '@/lib/ai/providers';
import { entitlementsByUserType } from '@/lib/ai/entitlements';
import { postRequestBodySchema, type PostRequestBody } from './schema';
import { geolocation } from '@vercel/functions';
import {
  createResumableStreamContext,
  type ResumableStreamContext,
} from 'resumable-stream';
import { after } from 'next/server';
import type { Chat } from '@/lib/db/schema';
import { differenceInSeconds } from 'date-fns';
import { ChatSDKError } from '@/lib/errors';

export const maxDuration = 60;

let globalStreamContext: ResumableStreamContext | null = null;

function createTextChunk(text: string): DataStreamString {
  const isAlreadyDataStreamString = /^[\da-k]:/.test(text);
  
  if (isAlreadyDataStreamString) {
    return text as DataStreamString;
  }

  return `0:${text}` as DataStreamString;
}


function getStreamContext() {
  if (!globalStreamContext) {
    try {
      globalStreamContext = createResumableStreamContext({
        waitUntil: after,
      });
    } catch (error: any) {
      if (error.message.includes('REDIS_URL')) {
        console.log(
          ' > Resumable streams are disabled due to missing REDIS_URL',
        );
      } else {
        console.error(error);
      }
    }
  }

  return globalStreamContext;
}

export async function POST(request: Request) {
  let requestBody: PostRequestBody;

  try {
    const json = await request.json();
    requestBody = postRequestBodySchema.parse(json);
  } catch (_) {
    return new ChatSDKError('bad_request:api').toResponse();
  }
  console.log(' > POST /chat', requestBody);

  try {
    const { id, message, selectedChatModel, selectedVisibilityType } =
      requestBody;

      const session = await auth();
      
      if (!session?.user) {
        return new ChatSDKError('unauthorized:chat').toResponse();
      }

    const userType: UserType = session.user.type;

    const messageCount = await getMessageCountByUserId({
      id: session.user.id,
      differenceInHours: 24,
    });

  
    if (messageCount > entitlementsByUserType[userType].maxMessagesPerDay) {
      return new ChatSDKError('rate_limit:chat').toResponse();
    }

    const chat = await getChatById({ id });
    if (!chat) {
      // const title = await generateTitleFromUserMessage({
      //   message,
      // });
      const title = 'Title from user message'; // Placeholder for title generation

      await saveChat({
        id,
        userId: session.user.id,
        title,
        visibility: selectedVisibilityType,
      });
    } else {
      if (chat.userId !== session.user.id) {
        return new ChatSDKError('forbidden:chat').toResponse();
      }
    }

    const previousMessages = await getMessagesByChatId({ id });

    const messages = appendClientMessage({
      // @ts-expect-error: todo add type conversion from DBMessage[] to UIMessage[]
      messages: previousMessages,
      message,
    });

    const { longitude, latitude, city, country } = geolocation(request);

    const requestHints: RequestHints = {
      longitude,
      latitude,
      city,
      country,
    };

    await saveMessages({
      messages: [
        {
          chatId: id,
          id: message.id,
          role: 'user',
          parts: message.parts,
          attachments: message.experimental_attachments ?? [],
          createdAt: new Date(),
        },
      ],
    });


    const streamId = generateUUID();
    await createStreamId({ streamId, chatId: id });
    const prompt = messages
      .filter((msg) => msg.role === 'user')
      .map((msg) => msg.content)
      .join('\n');

    // 🚀 3. Fetch from your FastAPI endpoint => proxy => ollama 
    const response = await fetch('http://localhost:8000/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        prompt,
        model: selectedChatModel,
      }),
    });

    if (!response.ok || !response.body) {
      throw new Error('Failed to fetch stream');
    }
    const assistantId = generateUUID();
    await saveMessages({
        messages: [
          {
            id: assistantId,
            chatId: id,
            role: 'user',
            parts: 'parts' in message ? message.parts : [],
            attachments: [],
            createdAt: new Date(),
          },
        ],
      });
    


    const stream = new ReadableStream({
      start(controller) {
        const encoder = new TextEncoder();
        const assistantId = generateUUID();

        // f: Start message
        controller.enqueue(encoder.encode(`f:{"messageId":"${assistantId}"}\n`));

        const reader = response.body!.getReader();
        const decoder = new TextDecoder();
        function read() {
          reader.read().then(({ done, value }) => {
            if (done) {
              // e: End step
              controller.enqueue(encoder.encode(`e:{"finishReason":"stop","isContinued":false}\n`));
              // d: Finish message
              controller.enqueue(encoder.encode(`d:{"finishReason":"stop","usage":{"promptTokens":1026,"completionTokens":73}}\n`));
              controller.close();
              return;
            }

            const chunk = decoder.decode(value, { stream: true });

            // Split into small parts (optional)
            const words = chunk.split(/(\s+|\n+)/);

            for (let i = 0; i < words.length; i++) {
              const word = words[i];
              if (word.trim()) {
                controller.enqueue(encoder.encode(`0:"${word} "\n`));
              }
            }

            read();
          });
        }

        read();
      },
    });

return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
    },
  });

  } catch (error) {
    if (error instanceof ChatSDKError) {
      return error.toResponse();
    }
  }

}


async function* fetchCustomStream(prompt: string, selectedChatModel: string, ): AsyncGenerator<string> {
  const response = await fetch('http://localhost:3000/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      prompt,
      model: selectedChatModel,
      // systemPrompt: systemPrompt(...),
    }),
  });

  if (!response.ok) throw new Error('Stream failed');

  const reader = response.body?.getReader();
  const decoder = new TextDecoder();
  let done = false;

  while (!done) {
    const { value, done: streamDone } = await reader!.read();
    done = streamDone;
    if (value) {
      yield decoder.decode(value, { stream: true });
    }
  }
}


export async function GET(request: Request) {
  const streamContext = getStreamContext();
  const resumeRequestedAt = new Date();

  if (!streamContext) {
    return new Response(null, { status: 204 });
  }

  const { searchParams } = new URL(request.url);
  const chatId = searchParams.get('chatId');

  if (!chatId) {
    return new ChatSDKError('bad_request:api').toResponse();
  }

  const session = await auth();

  if (!session?.user) {
    return new ChatSDKError('unauthorized:chat').toResponse();
  }

  let chat: Chat;

  try {
    chat = await getChatById({ id: chatId });
  } catch {
    return new ChatSDKError('not_found:chat').toResponse();
  }

  if (!chat) {
    return new ChatSDKError('not_found:chat').toResponse();
  }

  if (chat.visibility === 'private' && chat.userId !== session.user.id) {
    return new ChatSDKError('forbidden:chat').toResponse();
  }

  const streamIds = await getStreamIdsByChatId({ chatId });

  if (!streamIds.length) {
    return new ChatSDKError('not_found:stream').toResponse();
  }

  const recentStreamId = streamIds.at(-1);

  if (!recentStreamId) {
    return new ChatSDKError('not_found:stream').toResponse();
  }

  const emptyDataStream = createDataStream({
    execute: () => {},
  });

  const stream = await streamContext.resumableStream(
    recentStreamId,
    () => emptyDataStream,
  );

  /*
   * For when the generation is streaming during SSR
   * but the resumable stream has concluded at this point.
   */
  if (!stream) {
    const messages = await getMessagesByChatId({ id: chatId });
    const mostRecentMessage = messages.at(-1);

    if (!mostRecentMessage) {
      return new Response(emptyDataStream, { status: 200 });
    }

    if (mostRecentMessage.role !== 'assistant') {
      return new Response(emptyDataStream, { status: 200 });
    }

    const messageCreatedAt = new Date(mostRecentMessage.createdAt);

    if (differenceInSeconds(resumeRequestedAt, messageCreatedAt) > 15) {
      return new Response(emptyDataStream, { status: 200 });
    }

    const restoredStream = createDataStream({
      execute: (buffer) => {
        buffer.writeData({
          type: 'append-message',
          message: JSON.stringify(mostRecentMessage),
        });
      },
    });

    return new Response(restoredStream, { status: 200 });
  }

  return new Response(stream, { status: 200 });
}

export async function DELETE(request: Request) {
  const { searchParams } = new URL(request.url);
  const id = searchParams.get('id');

  if (!id) {
    return new ChatSDKError('bad_request:api').toResponse();
  }

  const session = await auth();

  if (!session?.user) {
    return new ChatSDKError('unauthorized:chat').toResponse();
  }

  const chat = await getChatById({ id });

  if (chat.userId !== session.user.id) {
    return new ChatSDKError('forbidden:chat').toResponse();
  }

  const deletedChat = await deleteChatById({ id });

  return Response.json(deletedChat, { status: 200 });
}
