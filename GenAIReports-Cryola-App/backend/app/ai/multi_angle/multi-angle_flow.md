# Multi-Angle Execution Flow Diagram
Models Used:
1. Reasoning : "o3"
2. Image Model : "gpt-image-1.5"

[ START PIPELINE ]
      |
      |          [ RETRY LOOP START ]                                                
      +-------------------------+------------------------+       
      | PARALLEL EXECUTION      |                        |       
      v                         v                        |       
[ GENERATE L2R IMAGES ]   [ GENERATE STRAIGHT IMAGES ]   |       
(Async Batch: 3 Variants) (Async Batch: 3 Variants)      |       
      |                         |                        |       
      +-----------+-------------+                        |       
                  | Await Completion                     |       
                  v                                      |       
[ EVALUATE L2R BATCH ] (Async Concurrent Critics)        |       
      |                                                  |       
      v                                                  |       
[ EVALUATE STRAIGHT BATCH ] (Async Concurrent Critics)   |       
      |                                                  |       
      v                                                  |       
[ CHECK THRESHOLDS & FEEDBACK ]                          |       
      |                                                  |       
   L2R Score >= 85? ------------------> [DONE]           |       
   (If No: Update Prompt with Feedback)                  |       
      |                                                  |       
   Straight Score >= 80? -------------> [DONE]           |       
   (If No: Update Prompt with Feedback)                  |       
      |                                                  |       
      v                   [Failed view goes for Regen]   |       
[ LOOP CONDITION CHECK ] --------------------------------+       
      | (If NOT all done AND Retries left)                       
      |                                                          
      | (If All Done OR Max Retries reached)                     
      v                                                          
[ SELECT BEST CANDIDATES ] (Top 1 L2R, Top 1 Straight)           
      |                                                          
      v                                                          
[ RETURN FINAL RESULTS ]                                         

