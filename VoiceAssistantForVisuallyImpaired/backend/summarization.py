#summarization
from transformers import TFBartForConditionalGeneration
from transformers import AutoTokenizer

def summarize_text(text, max_length=512):
    """Summarizes text using BART model with truncation."""
    tokenizer = AutoTokenizer.from_pretrained("facebook/bart-base")
    model = TFBartForConditionalGeneration.from_pretrained("facebook/bart-base")

    truncated_text = text[:max_length]  # Truncate if text exceeds max_length

    inputs = tokenizer([truncated_text], return_tensors='tf')
    outputs = model.generate(**inputs)
    summary = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return summary[:200]  # Limit summary length to 200 characters
