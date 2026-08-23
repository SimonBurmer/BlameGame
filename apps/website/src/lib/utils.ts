import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

/** The class-name helper every Aceternity component imports from `@/lib/utils`. */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * The page's content column.
 *
 * One value, used by every section, and the same one the navbar is given — so
 * nothing on the page is narrower than the header sitting above it. Wide on
 * purpose: the screenshots and the photo wall are the argument, and they want
 * the room.
 */
export const shell = 'mx-auto w-full max-w-[88rem] px-6 lg:px-10';

/**
 * The vertical rhythm between sections.
 *
 * One value, so no two sections breathe differently — the page reads as a
 * sequence rather than as a stack of components that each brought their own
 * padding.
 */
export const band = 'py-28 sm:py-40';
