from enum import IntEnum

class QuestBoosterType(IntEnum):

    ShowInitialCharacters = 1,
    ShowVowels = 2,
    ShowCorrectCharacters = 3,
    ShowContextParagraphs = 4,
    FilterCorrectCharactersOnKeyboard = 5,

    Add1Chance = 11,
    Add2Chances = 12,

    Add1Live = 21,
    Add3Lives = 22,
    Add9Lives = 23,
    FillAllLiveSlots = 25

