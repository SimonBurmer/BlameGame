import type { Messages } from './types';

export const de: Messages = {
  htmlLang: 'de',
  ogLocale: 'de_DE',
  meta: {
    title: 'Blame Game — errate, wessen Foto das ist',
    description:
      'Ein Partyspiel für 2–12 Leute. Alle werfen Fotos aus ihrer Galerie in einen Raum und raten dann, wem das Foto auf dem Bildschirm gehört. Wer schneller richtig liegt, bekommt mehr Punkte.',
    ogImageAlt: 'Blame Game — ein Foto im Fadenkreuz',
    keywords: [
      'Partyspiel',
      'Fotospiel',
      'Ratespiel',
      'Handyspiel für Gruppen',
      'Spiele mit Freunden',
      'Multiplayer Partyspiel',
    ],
  },
  nav: {
    howItWorks: 'So läuft es',
    features: 'Funktionen',
    faq: 'Fragen',
    languageLabel: 'Sprache',
    skipToContent: 'Zum Inhalt springen',
  },
  hero: {
    eyebrow: 'Partyspiel · 2–12 Leute · ein Handy pro Person',
    headline: 'Errate, wessen Foto auf dem Bildschirm ist.',
    sub: 'Alle werfen Fotos aus ihrer Galerie in einen Raum. Jede Runde taucht eines davon auf. Finde heraus, wem es gehört, bevor es jemand anderes tut — je schneller, desto mehr Punkte.',
    availability: 'Jetzt für iPhone',
    primaryCta: 'App Store',
    primaryCtaEyebrow: 'Laden im',
    secondaryCta: 'So läuft es ab',
  },
  stats: [
    { value: 12, suffix: '', label: 'Leute pro Raum' },
    { value: 10, suffix: '', label: 'Fotos pro Person' },
    { value: 5, suffix: '', label: 'Zeichen im Code' },
  ],
  shots: {
    heading: 'So sieht es aus',
    sub: 'Direkt vom Handy, mitten im Spiel.',
    items: [
      { file: 'lobby', caption: 'Code vorlesen und zuschauen, wer reinkommt', alt: 'Die Lobby mit Spielcode und fünf beigetretenen Personen' },
      { file: 'round', caption: 'Ein Foto, eine Uhr, fünf Verdächtige', alt: 'Eine laufende Runde mit Foto und den anderen Mitspielenden zur Auswahl' },
      { file: 'guessed', caption: 'Festlegen, bevor die Zeit es tut', alt: 'Ein abgegebener Tipp mit hervorgehobener Person' },
      { file: 'reveal', caption: 'Und dann die Auflösung', alt: 'Die Auflösung nennt, wem das Foto gehört' },
      { file: 'results', caption: 'Jemand muss gewinnen', alt: 'Die Endrangliste mit Punkten für alle' },
    ],
  },
  steps: {
    heading: 'Es passieren drei Dinge',
    items: [
      {
        title: 'Jemand eröffnet einen Raum',
        body: 'Eine Person erstellt das Spiel und liest einen fünfstelligen Code vor. Kein Konto, keine Anmeldung — alle anderen tippen einen Namen ein und sind dabei.',
      },
      {
        title: 'Alle steuern Fotos bei',
        body: 'Die App wählt zufällig Fotos aus deiner Galerie. Du siehst die Auswahl und kannst neu mischen, bevor irgendetwas hochgeladen wird — bis zu zehn pro Person, und das Spiel startet erst, wenn mindestens zwei Leute etwas beigesteuert haben.',
      },
      {
        title: 'Ihr ratet, wem es gehört',
        body: 'Ein Foto erscheint, die Uhr läuft. Tippe auf die Person, der es deiner Meinung nach gehört. Die Runde endet, sobald alle geantwortet haben — danach wird aufgelöst.',
      },
    ],
  },
  features: {
    heading: 'Was drinsteckt',
    sub: 'Gebaut als echtes Mehrspielerspiel und nicht als Quiz, bei dem zufällig Freunde dabeisitzen.',
    items: [
      {
        title: 'Bis zu zwölf Mitspielende',
        body: 'Ein Raum, ein Handy pro Person. Zu zweit geht es, richtig gut wird es ab etwa fünf — wenn sich niemand mehr ausschließen lässt.',
      },
      {
        title: 'Die Zeit läuft auf dem Server',
        body: 'Jede Runde endet für alle im selben Moment, und die Punkte werden aus der Serveruhr berechnet, nicht aus deiner. Eine falsch gehende Handyuhr verschafft niemandem einen Vorteil.',
      },
      {
        title: 'Erst schauen, dann hochladen',
        body: 'Die Fotos werden für dich ausgewählt, aber du siehst sie und kannst neu mischen, bevor sie dein Handy verlassen. Nichts geht ungefragt raus.',
      },
      {
        title: 'Hardcore-Modus',
        body: 'Vorschau aus: Was die Zufallsauswahl erwischt hat, sehen alle — du selbst zum ersten Mal auf dem Bildschirm der anderen. Für Gruppen, denen Zögern als Schummeln gilt.',
      },
      {
        title: 'Revanche mit einem Tipp',
        body: 'Sobald die Rangliste steht, kann dieselbe Runde direkt weiterspielen, ohne noch einmal Codes auszutauschen.',
      },
      {
        title: 'iPhone-Fotos funktionieren einfach',
        body: 'HEIC, JPEG und PNG lassen sich alle hochladen. Kein Umwandeln, kein „Format nicht unterstützt“ mitten im Spiel.',
      },
    ],
  },
  faq: {
    heading: 'Fragen',
    items: [
      {
        question: 'Brauche ich ein Konto?',
        answer:
          'Nein. Du tippst einen Namen und einen Raumcode ein und bist dabei. Es gibt nichts anzumelden und nichts zu merken.',
      },
      {
        question: 'Welche meiner Fotos landen im Spiel?',
        answer:
          'Die App wählt bis zu zehn zufällig aus deiner Galerie. Du siehst die Auswahl und kannst sie neu mischen, bevor etwas hochgeladen wird — es taucht also nichts auf, das du nicht vorher gesehen hast.',
      },
      {
        question: 'Wie viele Leute können mitspielen?',
        answer:
          'Zwei bis zwölf. Zu zweit geht es, aber ab vier wird es deutlich besser, weil das Raten erst dann wirklich schwer wird.',
      },
      {
        question: 'Was ist der Hardcore-Modus?',
        answer:
          'Die freiwillige Variante ohne Vorschau. Was die Zufallsauswahl aus deiner Galerie gezogen hat, geht direkt in den Raum — du siehst es zum ersten Mal, wenn es alle sehen.',
      },
      {
        question: 'Was kostet es?',
        answer:
          'Der Download ist kostenlos. Es gibt kein Konto und nichts einzurichten — Name eintippen, Code beitreten, spielen.',
      },
    ],
  },
  cta: {
    heading: 'Hol alle in einen Raum.',
    body: 'Kostenlos. Kein Konto, kein Aufwand — nur ein vorgelesener Code und das, was ohnehin auf deinem Handy liegt.',
  },
  footer: {
    tagline: 'Errate, wessen Foto das ist.',
    builtWith: 'Gebaut mit Flutter und FastAPI.',
  },
};
