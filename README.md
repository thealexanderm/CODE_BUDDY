# Code Buddy ☺ - AI-Powered Code Profiler

<p>Authors: Caleb Peters, Matt Simone, Alex Mulder<br>
Institution: Grand Valley State University<br>
Course: CIS 350</p>

## 1. Abstract

Software development takes time and effort to do well, but **Code Buddy** aims to ease the task for developers of all skill-levels. **Code Buddy** is a website designed to help programmers create better code. Users simply upload their code and the code will be analyzed by AI to offer suggestions including Big O analysis, identified flaws, comments, and coding conventions. Then, the user will be able to download the refactored code and the provided README. **Code Buddy** will not only save time, but it will also save developers from headaches by identifying flaws and possible bottlenecks before they arise.

## 2. Introduction

Large Language Models have changed the way that software is developed, but trying to "vibe code" can easily turn into fighting with the model rather than creating quality software. Even if you code something functional with an LLM, it may be riddled with bugs and security risks. **Code Buddy** aims to use AI to build code faster and better without the headaches.

**Code Buddy** is an intelligent source code analysis website built with Streamlit and powered by Groq (Llama 3.3). Once the user uploads their code, Groq will analyze it for time and space complexity, performance bottlenecks, security concerns, and style convention violations. Our website will return the report with detailed explanations, a README file, and a new version of the code with corrected errors and improved readability. The user will be able to export the refactored code and documentation instantly.

## 3. Architectural Design

The **Code Buddy** website is built entirely with Python. The frontend uses the Streamlit library. The backend implements the LLM prompts, API integration with GroqCloud, and JSON response validation. The website takes in the user's pasted code to give to the Groq Llama 3.3 model to analyze. The Groq Llama 3.3 model returns a detailed report with explanations, a README file, and a new version of the code with corrected errors and improved readability. The user will be able to export the refactored code and documentation instantly.

### 3.1 Class Diagram

<p align="center">
    <img src="UML/class_diagram.png" alt="Use Case Diagram" />
    Figure 1: Class Diagram
</p>

### 3.2 Use Case Diagram

<p align="center">
    <img src="UML/usecase_diagram.png" alt="Use Case Diagram" />
    Figure 2: Use Case Diagram
</p>

### 3.3 Sequence Diagram

<p align="center">
    <img src="UML/sequence_diagram.png" alt="Sequence Diagram" />
    Figure 3: Sequence Diagram
</p>

## 4. User Guide/Implementation

Users can access the application from any device with a web browser and internet connection. However, the application is designed for a desktop environment, so it is recommended to use "desktop mode" if using a mobile browser. If the application has not been accessed recently, it will need to "wake up"; this is normal and should only take around 15 seconds. The application can be accessed at the site: [code-buddy-mulderfork.streamlit.app](https://code-buddy-mulderfork.streamlit.app/).

<p align="center">
    <img src="Images/sleeping.png" alt="Sleeping site" />
    Figure 4: Sleeping Application
</p>

<p align="center">
    <img src="Images/codebuddy_site.png" alt="Code Buddy Site" />
    Figure 5: Code Buddy Site
</p>

Users can then paste their code into the input box and click "Analyze & Refactor". This will run the code analysis. Once the code analysis has run, users can open the expander boxes to read the complexity, identified flaws, suggestions, and generated README. Users may also scroll down to find the buttons to download the README as an Markdown file and the refactored code as a file corresponding to the uploaded language.

<p align="center">
    <img src="Images/user_input1.png" alt="Site with user input" />
    Figure 6: Code Buddy Code Analysis
</p>

<p align="center">
    <img src="Images/user_input2.png" alt="Site with user input" />
    Figure 7: Code Buddy Refactored Code and Generated README
</p>

## 5. Risk Analysis and Retrospective

Issues in the beginning of the project were prompt injections and hallucinations. These risked returning broken code to the user. In order to solve this issue, we used the LLM to re-analyze the analysis while being wary of managing our API rate limits.

Later in the development, we struggled with our continuous integration automation. Almost all of our code was prevented from being deployed due to linting issues. We dealt with this by making sure we used the same version of linting as the CI so that we could see the issues before we push the code.

In the final phase of our project, our biggest issue was updating our unit tests to reflect changes in our code. We changed the architecture of our project which caused our unit tests to no longer function. We fixed this by updating our unit tests to reflect the new architecture.

It would have been better if we had anticipated the risk of hallucinations and prompt injections in the design phase of our prototype, so we could have already had a plan to mitigate the vulnerability. Furthermore, given more time, we could implement more robust mitigation of the prompt injection and hallucination risks. Next time, we will also know to use static versions of the lint checkers rather than the latest versions. Finally, in the future, we will know to run unit tests before pushing the code.

## 6. Future Scope

Due to time constraints, we were not able to implement all the features that we had in mind. In the future, we would like to allow the user to upload a file of their code for analysis along with the option to paste it. We would also like to include syntax highlighting and line numbers to the code input box. Finally, we would like to implement an options menu where the user can choose which aspects they would like **Code Buddy** to feature in the analysis.

## 7. Conclusion

**Code Buddy** has achieved the goal of providing AI powered code profiling. By allowing users to input their code for feedback and refactoring, software development is made easier and more efficient than before. We believe this site is a great tool to aid developers of all backgrounds and skill levels.

## 8. Demo

A demo of CodeBuddy can be found [in this video](https://drive.google.com/file/d/1P79SIrx0Czq-IJQZPs77u6bFWoPD2eHR/view?usp=sharing).
