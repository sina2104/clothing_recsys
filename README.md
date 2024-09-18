# Clothing recommendation system


### Introduction
This is a streamlit application to show the results of the recommendation system.

---
### How to run it?
To run the application, simply copy and paste the following code to your terminal:
You will need to first upload the data from kaggle and after that you can run streamlit.
```shell
git clone https://github.com/sina2104/Furniture_detection
pip install -r requirements.txt
cd data
kaggle competitions download -c h-and-m-personalized-fashion-recommendations
unzip h-and-m-personalized-fashion-recommendations.zip
kaggle datasets download sinaaskary/submissions
unzip submissions.zip
cd ..
streamlit run app.py
```
### Example
https://github.com/user-attachments/assets/3b3364a4-e0de-499a-bf26-9f528b55f62e


### Different models reccomendations based on client's cart:
<table border="0">
 <tr>
    <td><b style="font-size:30px">Client's cart:</b></td>
    <td><b style="font-size:30px">Pairwise model:</b></td>
 </tr>
 <tr>
    <td><img src="https://github.com/user-attachments/assets/7aaa45ca-ea05-4315-b580-0a6924517fbe" width="500" /></td>
    <td><img src="https://github.com/user-attachments/assets/b746a580-b98b-426c-836e-6a9560974be2" width="500" /></td>
 </tr>
   <tr>
    <td><b style="font-size:30px">Resnet model:</b></td>
    <td><b style="font-size:30px">LGBM ranker model:</b></td>
 </tr>
 <tr>
    <td><img src="https://github.com/user-attachments/assets/76d3569b-2919-4edf-b48f-c68d3dd525c9" width="500" /></td>
    <td><img src="https://github.com/user-attachments/assets/a24395d9-4424-488c-bf27-10901fbff420" width="500" /></td>
 </tr>
</table>
