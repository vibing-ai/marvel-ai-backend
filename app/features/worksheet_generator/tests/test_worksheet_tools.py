import pytest
from app.features.worksheet_generator.tools import worksheet_generator, generate_course_type
from app.services.schemas import WorksheetQuestionModel
from langchain_core.documents import Document

def test_generate_course_type_valid():
   course_type = generate_course_type("Multivariable Calculus")

   assert isinstance(course_type, dict)
   assert len(course_type['course_type'])> 0
   assert course_type['course_type'] in ['Language and Literature', 'Language Acquisition', 'Individuals and Societies', 'Sciences', 'Mathematics', 'Arts']

def test_generate_course_type_invalid():
   course_type = generate_course_type("something random")

   assert isinstance(course_type, dict)
   assert len(course_type['course_type'])> 0
   assert course_type['course_type'] in ['None', 'None of the above']

def test_worksheet_generator_valid():
    docs = [Document(page_content="The image depicts a neural network architecture designed for speech recognition. The network is composed of two main branches: a Bidirectional Long Short-Term Memory (BiLSTM) branch and a Convolutional Neural Network (CNN) branch. The BiLSTM branch processes the input speech signal in the form of Mel-frequency cepstral coefficients (MFCC) sequence. This sequence is a representation of the speech signal's spectral characteristics over time. The BiLSTM layers analyze the temporal dependencies within the MFCC sequence, capturing the sequential patterns and features of the speech signal.", metadata={'source': 'https://www.pngitem.com/pimgs/m/633-6330418_deep-neural-network-architecture-deep-learning-architecture-diagram.png'}), Document(page_content="The CNN branch takes a spectrogram of the speech signal as its input. A spectrogram is a visual representation of the frequency content of a signal over time. The CNN layers extract spatial features from the spectrogram, learning to identify patterns and characteristics of the audio signal's frequency distribution. Both branches then converge, with the BiLSTM output and the CNN output being combined and fed into a series of fully connected layers. These layers perform a final classification based on the learned features from both branches, ultimately outputting a predicted label for the speech signal.", metadata={'source': 'https://www.pngitem.com/pimgs/m/633-6330418_deep-neural-network-architecture-deep-learning-architecture-diagram.png'}), Document(page_content="The network's architecture suggests that it combines the strengths of both BiLSTMs and CNNs. BiLSTMs excel at capturing temporal dependencies, while CNNs are effective at extracting spatial features. By combining these two approaches, the network can learn a comprehensive representation of the speech signal, leading to improved recognition accuracy. The image highlights the different stages of processing within the network, from the input speech signal to the final classification. It provides a visual understanding of how the network processes information and arrives at a prediction for the spoken word.", metadata={'source': 'https://www.pngitem.com/pimgs/m/633-6330418_deep-neural-network-architecture-deep-learning-architecture-diagram.png'})]
    worksheet_list = [
                WorksheetQuestionModel(
                    question_type = "fill_in_the_blank",
                    number = 2
                ),
                WorksheetQuestionModel(
                    question_type ="relate_concepts",
                    number = 1
                ),
                WorksheetQuestionModel(
                  question_type = "math_exercises",
                  number = 2
                )]
    worksheet = worksheet_generator('Mathematics', "College", worksheet_list, docs, "en", False)
   
    assert isinstance(worksheet, dict)
    assert len(worksheet) > 0

def test_worksheet_generator_invalid_document():
    docs = [] 
    worksheet_list = [
                WorksheetQuestionModel(
                    question_type = "fill_in_the_blank",
                    number = 2
                ),
                WorksheetQuestionModel(
                    question_type ="relate_concepts",
                    number = 1
                ),
                WorksheetQuestionModel(
                  question_type = "math_exercises",
                  number = 2
                )]
    with pytest.raises(ValueError) as exc_info:
        worksheet = worksheet_generator('Mathematics', "College", worksheet_list, docs, "en", False)
   
    assert isinstance(exc_info.value, ValueError)