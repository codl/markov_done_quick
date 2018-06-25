> Long time watcher, fifth time watching, first time watcher, first time Donating. It's gone ahead and put this $25 for each time.

> May I suggest we kill cancer!

> Greeting from Norway! And of course Save the animals. Kill the animals

## install

```sh
pipenv sync
# or, if you don't have pipenv
pip install -r requirements.txt
```

## scrape

```sh
python main.py scrape
```

the scraper is real messy right now and crashes sometimes
and does not detect when it's gone past the last page of donations

theres a messages.csv included already containing all donations up to
during 2018-06-24 evening-ish

## build model

```sh
python main.py build-model
```

## run

```sh
python main.py say
```

some sample output is included at [sample.txt](/sample.txt) if you
can't be bothered to do any of these things
