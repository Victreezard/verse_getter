# Overview
A collection of Python scripts for OBS that update text sources with bible verses

# verse_getter
## Retrieve bible verses from [Bible Display API](https://ibibles.net/m/quote03.htm)
  1. Enter the following:
     - *Text Source* - OBS Text Source to update
     - *Version* - Bible Version
     - *Book* - Book from the Bible
     - *Chapter & Verse* - Chapter and Verse of the book (Separated by space)
  2. Click *Get Verse*
  ![getter](https://user-images.githubusercontent.com/14161440/203757619-2cbe306e-6c33-4e5c-8502-d25ac849c01e.gif)

## Move from one verse to another
  1. Click *Next Verse* or *Prev Verse* to cycle through verses of the same book and chapter
  ![getter_nextprev](https://user-images.githubusercontent.com/14161440/203758749-ac15f8d8-e26a-4b82-bb60-2fdcc5009c81.gif)

# verse_otd
## Retrieve the verse of the day from [BibleGateway](https://www.biblegateway.com/usage/votd)
  1. Enter the following:
     - *Text Source* - OBS Text Source to update
     - *Version* - Bible Version
  2. Click *Get Verse*
  ![votd](https://user-images.githubusercontent.com/14161440/203759868-866c671f-57a6-4a95-b1d3-ff6edcdbfecc.gif)

# Environment
This script was developed and tested using the following:
 - Python 3.10.8
 - OBS 28.1.2
