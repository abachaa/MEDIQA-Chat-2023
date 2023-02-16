# MEDIQA-Chat-2023

- **Website**: https://sites.google.com/view/mediqa2023/clinicalnlp-mediqa-chat-2023 
- **Google group**: https://groups.google.com/g/mediqa-nlp

## Tasks
- **Task A - Short Dialogue2Note Summarization**: generating a section summary (section header and content) associated with the short input conversation. Section header will be one of twenty normalized section labels provided with the training data. 
- **Task B - Full Dialogue2Note Summarization**: generating a clinical note from the full input conversation. The note should include all relevant sections. Accepted first-level section headers are: "HISTORY OF PRESENT ILLNESS", "PHYSICAL EXAM", "RESULTS", "ASSESSMENT AND PLAN". 
- **Task C - Note2Dialogue Generation**: generating a doctor-patient conversation from the full input note. This task addresses data augmentation through the generation of synthetic conversations from clinical notes. We encourage the participants to apply the models developed for this task to generate additional data for tasks A & B. Task C will be evaluated with i) automatic evaluation metrics and ii) downstream impact when using the shared models to perform data augmentation and train note generation models. 

For all tasks, we encourage participants to try different and original approaches to contribute to the community with new research insights. All participating teams will be invited to submit papers describing their models and methods to the ClinicalNLP workshop at ACL 2023. 

## Datasets 

**Training & Validation Sets:** Released to the registered participants on February 10, 2023. 

**Test Sets:** Will be made available to the participants on March 15, 2023. 

## Submission Instructions

- Each team is allowed to submit a maximum of 3 runs for each task.
- Each team is required to submit the code/models used to generate the outputs. 
- Each run file should be named as follows: task{A|B|C}_teamName_run{1|2|3}.csv
- Task A Format: The run file should be a csv file with 3 columns: "TestID", "SystemOutput1", and "SystemOutput2". 
  - SystemOutput1 is the generated note section header. 
  - SystemOutput2 is the generated note section content (summary of the conversation).
- Format for tasks B & C: The run file should be a csv file with 2 columns: "TestID" and "SystemOutput".
  - For task B: SystemOutput is the full clinical note including the four main sections.
  - For task C: SystemOutput is the full conversation associated with the input note. The doctor and patient turns should start with "Doctor:" and "Patient:" (without quotes).
  
- Please use the submission_checker.py script to check and validate your run file before submission.
- The submission forms will be made available with the release of the test sets on March 15, 2023. 
- We will provide more guidelines on preparing and submitting the codes/models for confirmation of the results and additional downstream evaluation.
- After the competition, we encourage the teams to release their codes publicly with the publication of their papers. 


## Evaluation Methods
- For the three tasks, we will use ensemble metrics that correlate well with human judgments. 
- These ensemble metrics combine SOTA evaluation metrics including ROUGE, BERTScore and BLEURT. 
- An additional downstream evaluation will be performed for task C. 

## Scripts

- Script for submission format checking => scripts/submission_checker.py
- Script for task  A/B evaluation => scripts/evaluate_summarization.py

- Script for creating the virtual environment for using the evaluation script => scripts/install_evalvenv.sh
- Script for task B/C source/tgt data creation => scripts/divide_and_output_files.py

## Submission & Evaluation Process
- The training, validation and test sets will be released according to the schedule below. 
- Participants will have access to the submission forms on March 15 to submit their runs and codes.  
- Organisers will evaluate the submissions and release the results to the participants on March 31.
- Results will be considered official after submitting a working notes paper describing the used methods to the ACL-ClinicalNLP 2023 workshop. 

## Schedule

- All deadlines are 11:59PM UTC-12:00 (anywhere on Earth)
- Release of the training and validation sets: February 10, 2023
- Registration ends: March 3rd, 2023
- Release of the test sets: March 15, 2023 
- Run & code submission deadline: March 17, 2023
- Release of the official results by the organizers: March 31, 2023
- Paper submission deadline: May 2, 2023
- Notification of acceptance: May 22, 2023
- Camera-ready paper due: June 6, 2023
- Pre-recorded video due: June 12, 2023
- ACL-ClinicalNLP Workshop: July 14, 2023, Toronto, Canada


## Organizers: 

- Asma Ben Abacha, Microsoft, USA
- Wen-wai Yim, Microsoft, USA
- Griffin Adams, Columbia University, USA
- Neal Snider, Microsoft/Nuance, USA
- Meliha Yetisgen, University of Washington, USA
