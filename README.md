# Scrapper

Developed as part of my independent research in Nepali language. Kudos to [Nepali-NLP-Group](https://github.com/Nepali-NLP-Group).

## Dependencies

    $ pip install -r requirements.txt


### How to run

	$ python ekantipur.py -st 2019/01/01 -et 2019/06/01			     
			     
### Note:
 - Currently works for
 	- ekantipur
	- onlinekhabar
 - Start date and end date should be format YYYY/MM/DD
 - Start date should be earlier one compared to end date
 

### Output folder structure
	source
		category_1
			date_1.json
			date_2.json
			.
		category_2
			date_1.json
			date_2.json
			.
### To do:

- [x] Add logger
- [x] Add timer
- [ ] Add flexibility to download other news sites

