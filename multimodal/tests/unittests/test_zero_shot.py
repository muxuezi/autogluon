from PIL import Image
import requests
import pytest
from autogluon.multimodal import MultiModalPredictor


def test_clip_zero_shot():
    url = "http://images.cocodataset.org/val2017/000000039769.jpg"
    image = Image.open(requests.get(url, stream=True).raw)
    cat_image_name = "cat.jpg"
    image.save(cat_image_name)

    url = "https://farm1.staticflickr.com/29/57154382_07b25134f7_z.jpg"
    image = Image.open(requests.get(url, stream=True).raw)
    dog_image_name = "dog.jpg"
    image.save(dog_image_name)

    cat_text = "a photo of a cat"
    dog_text = "a photo of a dog"
    bird_text = "a photo of a bird"

    predictor = MultiModalPredictor(hyperparameters={"model.names": ["clip"]}, problem_type="zero_shot")

    # compute the cosine similarity of one image-text pair.
    pred = predictor.predict({"image": [cat_image_name], "text": [cat_text]})
    assert pred.shape == (1,)

    # compute the cosine similarities of more image and text pairs.
    pred = predictor.predict({"image": [cat_image_name, dog_image_name], "text": [cat_text, dog_text]})
    assert pred.shape == (2,)

    # match images in a given text pool and output the matched text index (starting from 0) for each image.
    pred = predictor.predict({"image0": [cat_image_name, dog_image_name]}, {"names": [dog_text, cat_text, bird_text]})
    assert pred.shape == (2,)

    # match texts in a given image pool and output the matched image index (starting from 0) for each text.
    pred = predictor.predict({"query": [dog_text, cat_text, bird_text]}, {"candidates": [cat_image_name, dog_image_name]})
    assert pred.shape == (3,)

    # predict the probabilities of one image matching several texts.
    prob = predictor.predict_proba({"image": [cat_image_name]}, {"text": [cat_text, dog_text, bird_text]})
    assert prob.shape == (1, 3)
    for per_row_prob in prob:
        assert pytest.approx(sum(per_row_prob), 1e-6) == 1

    # given two or more images, we can get the probabilities of matching each image with a pool of texts.
    prob = predictor.predict_proba({"image": [dog_image_name, cat_image_name]}, {"text": [bird_text, cat_text, dog_text]})
    assert prob.shape == (2, 3)
    for per_row_prob in prob:
        assert pytest.approx(sum(per_row_prob), 1e-6) == 1

    # predict the probabilities of one text matching several images.
    prob = predictor.predict_proba({"x": [cat_text]}, {"y": [dog_image_name, cat_image_name]})
    assert prob.shape == (1, 2)
    for per_row_prob in prob:
        assert pytest.approx(sum(per_row_prob), 1e-6) == 1

    # given two or more texts, we can get the probabilities of matching each text with a pool of images.
    prob = predictor.predict_proba({"a": [bird_text, cat_text, dog_text]}, {"b": [dog_image_name, cat_image_name]})
    assert prob.shape == (3, 2)
    for per_row_prob in prob:
        assert pytest.approx(sum(per_row_prob), 1e-6) == 1

    # extract image embeddings.
    embedding = predictor.extract_embedding({"123": [dog_image_name, cat_image_name]})
    assert list(embedding.keys()) == ["123"]
    for v in embedding.values():
        assert v.shape == (2, 512) or v.shape == (2, 768)

    # extract text embeddings.
    embedding = predictor.extract_embedding({"xyz": [bird_text, dog_text, cat_text]})
    assert list(embedding.keys()) == ["xyz"]
    for v in embedding.values():
        assert v.shape == (3, 512) or v.shape == (3, 768)

    # extract embeddings for both images and texts.
    embedding = predictor.extract_embedding({"image": [cat_image_name, dog_image_name], "text": [bird_text, dog_text]})
    assert list(embedding.keys()).sort() == ["image", "text"].sort()
    for v in embedding.values():
        assert v.shape == (2, 512) or v.shape == (2, 768)

    # invalid API usage 1: passing one dictionary, but different keys have inconsistent list lengths.
    with pytest.raises(ValueError):
        pred = predictor.predict({"image": [cat_image_name, dog_image_name], "text": [cat_text]})

    with pytest.raises(ValueError):
        embedding = predictor.extract_embedding({"image": [cat_image_name], "text": [cat_text, bird_text]})

    # invalid API usage 2: predicting probability with only one dictionary as input.
    with pytest.raises(AssertionError):
        prob = predictor.predict_proba({"image": [cat_image_name], "text": [cat_text]})
