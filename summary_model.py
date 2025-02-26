import torch
from transformers import T5Tokenizer, T5ForConditionalGeneration, TrainingArguments, Trainer, DataCollatorForSeq2Seq
from datasets import load_dataset

# Step 1: Load a Subset of Samsum Dataset for Faster Training
dataset = load_dataset("samsum", trust_remote_code=True)

# Use only a smaller subset to speed up training
subset_size = 10  # Adjust based on available resources
train_subset = dataset["train"].shuffle(seed=42).select(range(subset_size))
test_subset = dataset["test"].shuffle(seed=42).select(range(20))

# Step 2: Load T5 Tokenizer and Model
tokenizer = T5Tokenizer.from_pretrained("t5-small")
model = T5ForConditionalGeneration.from_pretrained("t5-small")

# Step 3: Tokenization Function
def tokenize_function(example):
    model_inputs = tokenizer(example["dialogue"], max_length=512, truncation=True, padding="max_length")
    with tokenizer.as_target_tokenizer():
        labels = tokenizer(example["summary"], max_length=128, truncation=True, padding="max_length")
    model_inputs["labels"] = labels["input_ids"]
    return model_inputs

# Step 4: Apply Tokenization to Dataset
train_dataset = train_subset.map(tokenize_function, batched=True)
test_dataset = test_subset.map(tokenize_function, batched=True)

# Step 5: Data Collator for Efficient Padding
data_collator = DataCollatorForSeq2Seq(tokenizer, model=model)

# Step 6: Training Arguments
training_args = TrainingArguments(
    output_dir="./chat_summarizer",
    evaluation_strategy="epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=4,  # Increase batch size if you have a GPU
    per_device_eval_batch_size=4,
    num_train_epochs=3,
    weight_decay=0.01,
    save_total_limit=2,
    fp16=True if torch.cuda.is_available() else False,  # Enable mixed precision if using GPU
    logging_dir="./logs",
    logging_steps=500,
)

# Step 7: Train the Model
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=test_dataset,
    tokenizer=tokenizer,
    data_collator=data_collator
)

trainer.train()

# Step 8: Save the Trained Model
model.save_pretrained("chat_summary_model")
tokenizer.save_pretrained("chat_summary_model")

# Step 9: Load Model for Summarization
model = T5ForConditionalGeneration.from_pretrained("chat_summary_model")
tokenizer = T5Tokenizer.from_pretrained("chat_summary_model")

# Step 10: Summarization Function
def summarize_chat(messages):
    """Generates a WhatsApp chat summary using the trained model."""
    inputs = tokenizer(messages, return_tensors="pt", truncation=True, max_length=512)
    summary_ids = model.generate(**inputs)
    return tokenizer.decode(summary_ids[0], skip_special_tokens=True)

# Step 11: Test with a Sample WhatsApp-like Chat
sample_chat = """
User1: Hey, let's meet at 6 PM.
User2: Sure, where?
User1: Cafe near my place.
User2: Sounds good!
"""

print("Chat Summary:", summarize_chat(sample_chat))
