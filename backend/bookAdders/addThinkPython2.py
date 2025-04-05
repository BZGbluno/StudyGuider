from InternalTools.VectorCreator import VectorEmbedder
from InternalTools.FunctionsToHelpBreakDownTextBook import pdfToString
from InternalTools.FunctionsToHelpBreakDownTextBook import removeAnythingBeforeContent
from InternalTools.FunctionsToHelpBreakDownTextBook import regex_text_splitter
from InternalTools.FunctionsToHelpBreakDownTextBook import regex_text_splitter
from InternalTools.FunctionsToHelpBreakDownTextBook import splitIntoChunks_to_MapToChapter
from InternalTools.FunctionsToHelpBreakDownTextBook import MapOfChapterWithChunks_to_DataFrame
from InternalTools.FunctionsToHelpBreakDownTextBook import RemoveAppendixFromFinalChapter
import pandas as pd

def main():


    textBookTitle = "thinkpython2"
    tableOfContents = ["The Way of the Program", "Variables, expressions and statements", "Functions",
                        "Case study: interface design", "Conditionals and recursion", "Fruitful functions",
                          "Iteration", "Strings", "Case study: word play", "Lists", "Dictionaries", "Tuples",
                            "Case study: data structure selection", "Files", "Classes and object", "Classes and functions",
                              "Classes and methods", "Inheritance", "The Goodies"]
    # breaking pdf into chunks
    pdfLocation = "./thinkpython2.pdf"
    combinedText = pdfToString(pdfLocation)
    removedContentText = removeAnythingBeforeContent(combinedText)
    listSplitByChapters = regex_text_splitter(removedContentText)

    listSplitByChapters = listSplitByChapters[1:]
    finalChapter = len(listSplitByChapters)-1
    chapterMap = RemoveAppendixFromFinalChapter(listSplitByChapters, finalChapter)
    chapterMap = splitIntoChunks_to_MapToChapter(listSplitByChapters)
    dataFrame = MapOfChapterWithChunks_to_DataFrame(chapterMap)

    
    for chapter, chapter_name in enumerate(tableOfContents, start=1):
        dataFrame.loc[dataFrame['chapter'] == chapter, 'Chapter_Name'] = chapter_name



    # making embedding vectors
    embedder = VectorEmbedder("sentence-transformers/all-MiniLM-L6-v2", dataFrame)
    embedder.createEmbeddings()
    embedder.printEmbeddings()


    newFrame = embedder.getEmbeddingsDf()
    newFrame.to_csv(f"./csv/{textBookTitle}.csv")

    
    




if __name__ == "__main__":
    main()

# python3 -m StudyGuider.bookAdders.ThinkPython2.addBook