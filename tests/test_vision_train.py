import pytest
from fastai import *
from fastai.vision import *

pytestmark = pytest.mark.integration

@pytest.fixture(scope="module")
def learn():
    path = untar_data(URLs.MNIST_TINY)
    data = ImageDataBunch.from_folder(path, ds_tfms=(rand_pad(2, 28), []), batch_size=16, num_workers=2)
    data.normalize()
    learn = ClassificationLearner(data, simple_cnn((3,16,16,16,2), bn=True), metrics=accuracy)
    learn.fit_one_cycle(3)
    return learn

def test_accuracy(learn):
    assert accuracy(*learn.get_preds()) > 0.9

def test_error_rate(learn):
    assert error_rate(*learn.get_preds()) < 0.1

def test_1cycle_lrs(learn):
    lrs = learn.recorder.lrs
    assert lrs[0]<0.001
    assert lrs[-1]<0.0001
    assert np.max(lrs)==3e-3

def test_1cycle_moms(learn):
    moms = learn.recorder.moms
    assert moms[0]==0.95
    assert abs(moms[-1]-0.95)<0.01
    assert np.min(moms)==0.85

def test_preds(learn):
    pass_tst = False
    for i in range(3):
        img, label = learn.data.valid_ds[i]
        pred_class,pred_idx,outputs = learn.predict(img)
        if outputs[label] > outputs[1-label]: return
    assert false, 'Failed to predict correct class'

def test_lrfind(learn):
    learn.lr_find(start_lr=1e-5,end_lr=1e-3, num_it=15)
