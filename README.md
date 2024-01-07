### EARNINGS CALL TRANSCRIPT ANALYSIS 
---------------------------------------------------------------------------------

### What is the Project all about?

Earnings calls are conference calls held by publicly traded companies, typically each quarter, to discuss their financial results and performance. These calls involve company executives, such as the CEO and CFO, presenting their prepared remarks and then participating in a Q&A session with analysts and investors.

Earnings call transcripts are written records of these calls, capturing the dialogue and information shared. They provide a detailed account of the company's financial performance, management's insights, and responses to questions from analysts and investors.

We believe that this information can be extracted and be of value to market participants by 
- deriving valuable insights rapidly.
- connecting the dots with existing company information.
- analyzing sentiments.

---------------------------------------------------------------------------------

### Use Case

When incorporating the entire project, it can become a product that enhances investment management processes. It can serve as a value adding data source for investors, traders, analysts, and portfolio managers.

---------------------------------------------------------------------------------

### How to Use?

_The information is to only use the current state of the project_

- Create a Database in MS SQL Server.
- Create a new table in that database using - `sql/tbl_TranscriptExtract.sql` file.
- Download a earning call transcript and save to `input/transcripts` folder or use any existing transcript.
- Input the DB server config and transcript filename in the config file - `input/config.json`.
- Run the script `transcript_pdf_to_text.py`.
- Check file - `extract.txt` for manual proof reading.
- Check DB table `{DB_Name}.dbo.TranscriptExtract` for the extracted data.

---------------------------------------------------------------------------------

### Future Scope 

**Sprint 1** - Extract QNA from listed companies quarterly meetings - Concall Transcripts.

**Sprint 2** - Sentiment Analysis.

**Sprint 3** - Find links in questions and answers of Transcripts for different periods.

The code in this repo is a raw start for Sprint 1 part of this project. It excludes optimization and the edge cases taken care of in the next iterations. Currently the project progress is at **Sprint 2** level. I am working with someone for the rest of the sprints. We think it can add value as a product to supplement the process investment management which is why we have decided to keep the rest of the project private.

---------------------------------------------------------------------------------