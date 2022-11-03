from transformers import AutoModelForQuestionAnswering, AutoTokenizer, pipeline

def basic():
    model_name = "deepset/roberta-base-squad2"

    # a) Get predictions
    QA_input = {
        'question': 'Why is model conversion important?',
        'context': 'The option to convert models between FARM and transformers gives freedom to the user and let people easily switch between frameworks.'
    }
    res = QA_input

    # b) Load model & tokenizer
    model = AutoModelForQuestionAnswering.from_pretrained(model_name)
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    print(res)

def get_file_as_str(filename):
    string = ""
    with open(filename, "r") as filename:
        for line in filename.readlines():
            string += line

    return string

class RobertaSquad():
    def __init__(self):
        self.model_name = "deepset/tinyroberta-squad2"
        self.nlp = pipeline('question-answering', model=self.model_name, tokenizer=self.model_name)
        self.qa_input = {
            'question': None,
            'context': None
        }
        self.model = AutoModelForQuestionAnswering.from_pretrained(self.model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.history = []

    def set_context(self, context):
        self.qa_input['context'] = context

    def get_answer(self, question):
        self.qa_input['question'] = question
        res = self.nlp(self.qa_input)
        res['question'] = self.qa_input['question']
        self.history.append(res)
        print(self.history)

if __name__ == "__main__":
    model = RobertaSquad()
    model.set_context(get_file_as_str("data_scraper/examples/toy_story.txt"))
    model.get_answer("Who is Woody?")
    model.get_answer("When was it released?")