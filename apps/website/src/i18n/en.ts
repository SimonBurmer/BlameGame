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
    availability: 'Out now on iPhone',
    primaryCta: 'App Store',
    primaryCtaEyebrow: 'Download on the',
    secondaryCta: 'See how it works',
    verdictBefore: 'It was',
    verdictAfter: '’s photo.',
    suspects: ['Mara', 'Jonas', 'Ada', 'Leo', 'yours'],
    scrollCue: 'Scroll',
  },
  moment: {
    heading: 'Ten seconds. One photo. Everybody looking at everybody.',
    sub: 'A picture nobody has thought about in two years goes up on five screens at once, and the clock starts. Somebody in the room took it. The scoring rewards the person who works out who first.',
    caption: 'One round, three phones.',
  },
  stats: [
    { value: 12, suffix: '', label: 'players in a room' },
    { value: 10, suffix: '', label: 'photos each' },
    { value: 5, suffix: '', label: 'characters in a code' },
  ],
  shots: {
    items: [
      { file: 'lobby', caption: 'Read out the code, watch everyone land', alt: 'The lobby, showing a game code and five players who have joined' },
      { file: 'round', caption: 'One photo, one clock, five suspects', alt: 'A round in progress with a photo and the other players to choose from' },
      { file: 'guessed', caption: 'Lock it in before the clock does', alt: 'A guess submitted, with the chosen player highlighted' },
      { file: 'reveal', caption: 'And then you find out', alt: 'The reveal, naming whose photo it was' },
      { file: 'results', caption: 'Somebody has to win', alt: 'The final leaderboard with scores for every player' },
    ],
  },
  steps: {
    heading: 'Three things happen',
    sub: 'Start to finish, a game is about ten minutes. There is nothing to set up and nothing to learn.',
    items: [
      {
        title: 'Someone starts a room',
        body: 'One player creates the game and reads out a five-character code. No accounts and no sign-up — everybody else types a name and joins.',
        shot: 'home',
        shotAlt: 'The start screen, with a name field, a create button and a Hardcore mode switch',
      },
      {
        title: 'Everyone adds photos',
        body: 'The app picks photos at random from your camera roll. You see what it chose and can reshuffle before anything is uploaded — up to ten each, and the game will not start until at least two people have contributed.',
        shot: 'lobby',
        shotAlt: 'The lobby, showing a game code and five players who have joined',
      },
      {
        title: 'You guess whose it is',
        body: 'A photo appears and the clock starts. Tap the person you think it belongs to. The round ends the moment everybody has answered, and then it tells you who was right.',
        shot: 'reveal',
        shotAlt: 'The reveal, naming whose photo it was',
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
        question: 'What does it cost?',
        answer:
          'Nothing to download. There is no account to make and nothing to set up — you type a name, join a code, and play.',
      },
    ],
  },
  cta: {
    heading: 'Get everyone in a room.',
    body: 'Free to download. No account, no setup — just a code read out loud and whatever is already on your phone.',
  },
  footer: {
    tagline: 'Guess whose photo it is.',
    builtWith: 'Built with Flutter and FastAPI.',
  },
};
