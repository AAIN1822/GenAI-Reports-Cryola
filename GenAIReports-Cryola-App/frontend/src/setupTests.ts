import "@testing-library/jest-dom";import { vi } from 'vitest';

/// <reference types="vitest" />
// Mock alert to avoid unhandled errors
globalThis.alert = vi.fn();