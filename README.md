# autocomplete-ngram-model
NLP Autocomplete N-Gram Model

## UI

```
cd ui
yarn install

export NODE_ENV=developement
yarn serve --mode $NODE_ENV
```

## API

```
cd ui/
uvicorn main:app --host 0.0.0.0 --port 8088 --reload
```

## Web Links

[API](http://0.0.0.0:8088)
[Docs](http://0.0.0.0:8088/docs)
[UI](http://localhost:8080/)

## Colab Notebook

https://colab.research.google.com/gist/Mageswaran1989/3e19b339477cc7acee67e9f1667978bf/autocorrectmodel.ipynb