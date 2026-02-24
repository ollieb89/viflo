'use strict';
const { defineConfig } = require('vitest/config');

module.exports = defineConfig({
  test: {
    include: ['bin/lib/__tests__/**/*.test.{js,cjs}'],
    environment: 'node',
    globals: true,
  },
});
