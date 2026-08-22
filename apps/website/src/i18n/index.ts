import { de } from './de';
import { en } from './en';
import type { Locale, Messages } from './types';

export const messages: Record<Locale, Messages> = { en, de };

export * from './types';
