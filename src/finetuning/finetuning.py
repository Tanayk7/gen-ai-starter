import json
from openai import OpenAI
from training import training_data
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

def generate_training_file(file_path='training.jsonl'):
    with open(file_path, 'w', encoding='utf8') as outfile:
        for entry in training_data:
            json.dump(entry, outfile, ensure_ascii=False)
            outfile.write('\n')

def create_finetune(): 
    file = client.files.create(
        file=open("./training.jsonl", "rb"),
        purpose="fine-tune"
    )
    print("created openai file: ", file)
    job = client.fine_tuning.jobs.create(
        training_file=file.id,
        model="gpt-4o-mini-2024-07-18"
    )
    print("Created finetuning job: ", job)

if __name__ == "__main__": 
    # generate_training_file()
    # print("generated training file!")
    create_finetune()