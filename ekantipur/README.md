# Scrapper

This is the script to scrap all the text from [Kantipur](https://ekantipur.com/) Nepal news website.


### How to run

	$ python scrapper.py -n https://ekantipur.com/ \
			     -s kantipur \
			     -st 2020/04/10 \
			     -et 2020/04/15

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
