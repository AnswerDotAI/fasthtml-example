# Data Spot Check Demo

We wanted to quickly look at some data before doing some BERT training.

This app downloads a sample of the data from a Hugging Face dataset.

It shows a random (unrated) sample. You can rate ("good", "ok" or "bad") and later download the ratings as a CSV. But the main purpose is just to give an excuse for looking at a bunch of samples to get a feel for what this dataset contains.

This one doesn't use any HTMX features. To rate you click a link, which takes you to "/rate/{id}/{label}". This stores the label then redirects you back to /rate to get another sample.