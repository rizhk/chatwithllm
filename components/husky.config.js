// husky.config.js
module.exports = {
  hooks: {
    'pre-commit': 'pnpm tsc --noEmit && pnpm lint',
  },
};