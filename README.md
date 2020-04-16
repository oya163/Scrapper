# Scrapper

Developed as part of my independent research in Nepali language. Kudos to [Nepali-NLP-Group](https://github.com/Nepali-NLP-Group).

## Dependencies

    $ pip install -r requirements.txt


### How to run

	$ python scrapper.py -n <news_link> \
			     -s <news_source> \
			     -st <start_date> \
			     -et <end_date>
			     
	$ python scrapper.py -n https://ekantipur.com/ \
			     -s kantipur \
			     -st 2020/04/10 \
			     -et 2020/04/15			     
			     
### Note:
 - Currently, works only for Kantipur
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

- [ ] Add logger
- [ ] Add timer
- [ ] Add flexibility to download other news sites

