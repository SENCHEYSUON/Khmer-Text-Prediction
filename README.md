# Khmer-Text-Prediction

## Description

This project aims to develop a system that predicts the next word or suggests possible words as
the user types in Khmer. Will investigate both statistical and deep learning approaches and
examine the challenges in predicting Khmer words due to spacing issues, compound structures,
and orthographic variants.

## Key Tasks

- Collect Khmer text corpus (news, social media, literature)
- Preprocess the data: tokenization, sentence segmentation.
- Compare models:
   - **N-gram language models**
   - **RNN/LSTM/GRU models**
   - **Transformer-based models (GPT-style, mBERT, mT5)**
- Implement a simple demo: keyboard auto-suggestion or sentence completion
- Evaluate accuracy and relevance of predictions

## Installation/Dev

1. Clone Repo
```bash
git clone https://github.com/SENCHEYSUON/Khmer-Text-Prediction.git
cd Khmer-Text-Prediction
```

2. Optional: Create virtual environment
```bash
python -m venv .venv --upgrade-deps
source .venv/bin/activate   # Linux / Mac
.venv\Scripts\activate      # Windows
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

## Reference Link's: 
- **awesome-khmer-language By SeangHay**: https://github.com/seanghay/awesome-khmer-language
- **Khmer-text-data By Phylypo**: https://github.com/phylypo/khmer-text-data/tree/master/oscar/seg_data
- **GRU Code Documentation**: https://docs.pytorch.org/docs/stable/generated/torch.nn.GRU.html
- **LSTM Code Documentation**: https://docs.pytorch.org/docs/stable/generated/torch.nn.LSTM.html
- **GoldFish Model_khm_khmr_5mb**: https://huggingface.co/goldfish-models/khm_khmr_5mb
- **GoldFish Model_khm_khmr_full**: https://huggingface.co/goldfish-models/khm_khmr_full
- **SeaLLMs/SeaLLM-7B-v2.5**: https://huggingface.co/SeaLLMs/SeaLLM-7B-v2.5

### Contact

- **SUON Senchey**: https://github.com/SENCHEYSUON
- **VEY Sreypich**: https://github.com/sreypich999
- **Sem Yuthearylyhour**: https://github.com/Lyhour7777
- **VORN Seavmey**: https://github.com/meyseav
- **VANNA Juuka**: https://github.com/vannajuuka


