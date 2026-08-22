import type { Messages } from './types';

export const en: Messages = {
  htmlLang: 'en',
  ogLocale: 'en_US',
  meta: {
    title: 'Blame Game — guess whose photo it is',
    description:
      'A party game for 2–12 players. Everyone drops photos from their camera roll into one room, then guesses whose photo is on screen. Faster correct answers score more.',
    ogImageAlt: 'Blame Game — a photo caught in a reticle',
    keywords: [
      'party game',
      'photo game',
      'guessing game',
      'camera roll game',
      'multiplayer party game',
      'games to play with friends',
    ],
  },
  nav: {
    howItWorks: 'How it works',
    features: 'Features',
    faq: 'FAQ',
    languageLabel: 'Language',
    skipToContent: 'Skip to content',
  },
  hero: {
    eyebrow: 'Party game · 2–12 players · one phone each',
    headline: 'Guess whose photo is on the screen.',
    sub: 'Everyone throws photos from their camera roll into one room. Each round, one of them appears. Work out who it belongs to before anybody else does — the faster you are, the more it is worth.',
    availability: 'In development. Not on the stores yet.',
    secondaryCta: 'See how it works',
  },
  steps: {
    heading: 'Three things happen',
    items: [
      {
        title: 'Someone starts a room',
        body: 'One player creates the game and reads out a five-character code. No accounts and no sign-up — everybody else types a name and joins.',
      },
      {
        title: 'Everyone adds photos',
        body: 'The app picks photos at random from your camera roll. You see what it chose and can reshuffle before anything is uploaded — up to ten each, and the game will not start until at least two people have contributed.',
      },
      {
        title: 'You guess whose it is',
        body: 'A photo appears and the clock starts. Tap the person you think it belongs to. The round ends the moment everybody has answered, and then it tells you who was right.',
      },
    ],
  },
  features: {
    heading: 'What is in it',
    sub: 'Built as an actual multiplayer game rather than a quiz that happens to have friends in it.',
    items: [
      {
        title: 'Up to twelve players',
        body: 'One room, one phone each. It works with two, but it comes alive somewhere around five, when nobody can rule anybody out.',
      },
      {
        title: 'The server keeps time',
        body: 'Every round ends at the same instant for everybody, and your score is worked out from the server’s clock rather than your phone’s. Nobody wins by having a wrong clock.',
      },
      {
        title: 'See the shuffle first',
        body: 'The photos are picked for you, but you get to look at them and reshuffle before they leave your phone. Nothing is uploaded behind your back.',
      },
      {
        title: 'Hardcore mode',
        body: 'Turn the preview off and whatever the shuffle picked is what the room sees. For groups who have decided that flinching is cheating.',
      },
      {
        title: 'Rematch in one tap',
        body: 'When the leaderboard lands, the same group can go straight into another round without swapping codes again.',
      },
      {
        title: 'iPhone photos just work',
        body: 'HEIC, JPEG and PNG all upload. No converting, no “unsupported format” halfway through a game.',
      },
    ],
  },
  faq: {
    heading: 'Questions',
    items: [
      {
        question: 'Do I need an account?',
        answer:
          'No. You type a name and a room code and you are in. There is nothing to sign up for and nothing to remember.',
      },
      {
        question: 'Which of my photos does it use?',
        answer:
          'The app samples up to ten at random from your camera roll. You see the selection and can reshuffle it before anything is uploaded, so you are never surprised by what turns up.',
      },
      {
        question: 'How many people can play?',
        answer:
          'Between two and twelve. Two works, but the game is better with four or more, because the guessing gets genuinely hard once nobody can be ruled out.',
      },
      {
        question: 'What is Hardcore mode?',
        answer:
          'The opt-in version where you do not get to preview the shuffle. Whatever it picked from your camera roll goes into the room, unseen by you until it is on everybody’s screen.',
      },
      {
        question: 'When can I download it?',
        answer:
          'It is still in development and there is no store listing yet. This page will carry the links when there are links to carry.',
      },
    ],
  },
  cta: {
    heading: 'Not out yet.',
    body: 'The game is being built in the open. When it reaches the App Store and Google Play, the buttons will appear right here.',
  },
  footer: {
    tagline: 'Guess whose photo it is.',
    builtWith: 'Built with Flutter and FastAPI.',
  },
};
