"""Retrieval evaluation on a labelled question set. Run: python evaluate.py"""
import json
from rag import KnowledgeBase
TESTS = [
("How much money do farmers get every year from PM-KISAN?","Kisan Samman"),("Who is eligible for PM Kisan Samman Nidhi?","Kisan Samman"),
("Which documents are needed for farmer income support of Rs 6000?","Kisan Samman"),
("Health insurance cover of 5 lakh per family under Ayushman Bharat","Jan Arogya"),("How to get Ayushman Bharat PM-JAY card?","Jan Arogya"),
("How to get a free LPG gas connection for poor women?","Ujjwala"),("Ujjwala Yojana eligibility","Ujjwala"),
("Pension of Rs 5000 per month after age 60 for unorganised workers","Atal Pension"),("What is the age limit for Atal Pension Yojana?","Atal Pension"),
("Life insurance Rs 2 lakh premium 436 per year","Jeevan Jyoti Bima"),("Accident insurance for Rs 20 per year","Suraksha Bima"),
("100 days guaranteed wage employment rural households","Rural Employment Guarantee"),
("Zero balance bank account for everyone","Jan Dhan"),
("Loan for SC ST and women entrepreneurs to start a new enterprise","Stand-Up"),
("Support for traditional artisans and craftspeople with toolkit","Vishwakarma"),
("Cash incentive for pregnant women for first child","Matru Vandana"),
("Crop insurance for farmers against natural calamities","Fasal Bima"),
("Credit card for farmers for short term agriculture loans","Kisan Credit Card"),
("Toilet construction incentive in rural areas","Swachh Bharat"),
("Where to file a complaint against a government department online?","CPGRAMS"),("What is the fee to file RTI?","Right to Information"),
]
kb = KnowledgeBase("data")
top1 = top3 = rr = 0
for q, exp in TESTS:
    titles = [t for _, t in kb.top_schemes(q, k=3)]
    rank = next((i + 1 for i, t in enumerate(titles) if exp.lower() in t.lower()), None)
    top1 += rank == 1; top3 += rank is not None; rr += 1 / rank if rank else 0
    if rank != 1: print("MISS@1:", q, "->", titles[0])
n = len(TESTS)
res = {"n": n, "top1": round(100 * top1 / n, 1), "top3": round(100 * top3 / n, 1), "mrr": round(rr / n, 3), "chunks": len(kb.chunks)}
json.dump(res, open("eval_results.json", "w")); print(res)
