# from fastapi import FastAPI, File, UploadFile, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import FileResponse, JSONResponse
# import pandas as pd
# import io
# import os
# from typing import List, Dict, Tuple, Optional
# from datetime import datetime
# import traceback
# import tempfile

# app = FastAPI(title="Insurance Payout Processor API")

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Update with your frontend URL
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # ===============================================================================
# # FORMULA DATA
# # ===============================================================================
# FORMULA_DATA = [
#     {"LOB": "PVT CAR", "SEGMENT": "PVT CAR COMP + SAOD", "PO": "90% of Payin", "REMARKS": "NIL"},
#     {"LOB": "PVT CAR", "SEGMENT": "PVT CAR TP", "PO": "90% of Payin", "REMARKS": "NIL"},
# ]

# # ===============================================================================
# # STATE MAPPING
# # ===============================================================================
# STATE_MAPPING = {
#     "ANDHRA PRADESH": "ANDHRA PRADESH",
#     "KRISHNA": "ANDHRA PRADESH",
#     "VIJAYWADA": "ANDHRA PRADESH",
#     "VIJAYAWADA": "ANDHRA PRADESH",
#     "VISAKHAPATNAM": "ANDHRA PRADESH",
#     "VIZAG": "ANDHRA PRADESH",
    
#     "KARNATAKA": "KARNATAKA",
#     "BANGALORE": "KARNATAKA",
#     "BENGALURU": "KARNATAKA",
#     "MYSORE": "KARNATAKA",
#     "MANGALORE": "KARNATAKA",
    
#     "KERALA": "KERALA",
#     "ERNAKULAM": "KERALA",
#     "COCHIN": "KERALA",
#     "KOCHI": "KERALA",
#     "TRIVANDRUM": "KERALA",
#     "CALICUT": "KERALA",
#     "KOZHIKODE": "KERALA",
    
#     "TAMIL NADU": "TAMIL NADU",
#     "CHENNAI": "TAMIL NADU",
#     "MADRAS": "TAMIL NADU",
#     "PONDICHERRY": "TAMIL NADU",
#     "PUDUCHERRY": "TAMIL NADU",
#     "COIMBATORE": "TAMIL NADU",
#     "MADURAI": "TAMIL NADU",
    
#     "TELANGANA": "TELANGANA",
#     "HYDERABAD": "TELANGANA",
#     "SECUNDERABAD": "TELANGANA",
    
#     "MAHARASHTRA": "MAHARASHTRA",
#     "MUMBAI": "MAHARASHTRA",
#     "PUNE": "MAHARASHTRA",
#     "NAGPUR": "MAHARASHTRA",
#     "THANE": "MAHARASHTRA",
#     "NASHIK": "MAHARASHTRA",
    
#     "DELHI": "DELHI",
#     "NEW DELHI": "DELHI",
#     "NCR": "DELHI",
    
#     "GUJARAT": "GUJARAT",
#     "AHMEDABAD": "GUJARAT",
#     "SURAT": "GUJARAT",
#     "VADODARA": "GUJARAT",
#     "RAJKOT": "GUJARAT",
    
#     "RAJASTHAN": "RAJASTHAN",
#     "JAIPUR": "RAJASTHAN",
#     "JODHPUR": "RAJASTHAN",
#     "UDAIPUR": "RAJASTHAN",
    
#     "UTTAR PRADESH": "UTTAR PRADESH",
#     "LUCKNOW": "UTTAR PRADESH",
#     "KANPUR": "UTTAR PRADESH",
#     "AGRA": "UTTAR PRADESH",
#     "VARANASI": "UTTAR PRADESH",
#     "NOIDA": "UTTAR PRADESH",
    
#     "WEST BENGAL": "WEST BENGAL",
#     "KOLKATA": "WEST BENGAL",
#     "CALCUTTA": "WEST BENGAL",
    
#     "MADHYA PRADESH": "MADHYA PRADESH",
#     "BHOPAL": "MADHYA PRADESH",
#     "INDORE": "MADHYA PRADESH",
    
#     "PUNJAB": "PUNJAB",
#     "CHANDIGARH": "CHANDIGARH",
#     "HARYANA": "HARYANA",
#     "GOA": "GOA",
#     "BIHAR": "BIHAR",
#     "PATNA": "BIHAR",
#     "JHARKHAND": "JHARKHAND",
#     "RANCHI": "JHARKHAND",
#     "ODISHA": "ODISHA",
#     "BHUBANESWAR": "ODISHA",
#     "ASSAM": "ASSAM",
#     "GUWAHATI": "ASSAM",
# }

# uploaded_files = {}

# # ===============================================================================
# # HELPER FUNCTIONS
# # ===============================================================================

# def cell_to_str(val) -> str:
#     """Safely convert ANY cell value (float NaN, None, int, str) to string."""
#     if val is None:
#         return ""
#     try:
#         if pd.isna(val):
#             return ""
#     except (TypeError, ValueError):
#         pass
#     return str(val).strip()


# def safe_float(value) -> Optional[float]:
#     """Safely convert value to float, handling percentages and invalid values."""
#     if value is None:
#         return None
#     try:
#         if pd.isna(value):
#             return None
#     except (TypeError, ValueError):
#         pass
    
#     s = str(value).strip().upper().replace("%", "")
#     if s in ["D", "NA", "", "NAN", "NONE", "DECLINE", "0.00%", "0.0%", "0%"]:
#         return None
    
#     try:
#         num = float(s)
#         if num < 0:
#             return None
#         # Convert decimals to percentages (0.28 -> 28%)
#         return num * 100 if 0 < num < 1 else num
#     except Exception:
#         return None


# def map_state(location: str) -> str:
#     """Map location/geo name to state using STATE_MAPPING."""
#     location_upper = location.upper()
    
#     # Direct match first
#     for key, val in STATE_MAPPING.items():
#         if key.upper() == location_upper:
#             return val
    
#     # Partial match
#     for key, val in STATE_MAPPING.items():
#         if key.upper() in location_upper:
#             return val
    
#     return location  # Return original if no match


# def calculate_payout(payin: float, lob: str = "PVT CAR", segment: str = "PVT CAR COMP + SAOD") -> Tuple[float, str, str]:
#     """
#     Calculate payout based on formula: 90% of Payin
#     """
#     if payin == 0 or payin is None:
#         return 0, "0% (No Payin)", "Payin is 0"
    
#     # Formula: 90% of Payin
#     payout = round(payin * 0.90, 2)
#     formula = "90% of Payin"
#     explanation = f"Applied formula: {formula} for {segment}"
    
#     return payout, formula, explanation


# # ===============================================================================
# # EXCEL PROCESSOR
# # ===============================================================================

# class ExcelProcessor:
#     """Process the insurance payout Excel sheet."""
    
#     @staticmethod
#     def process(content: bytes, sheet_name: str,
#                 override_enabled: bool = False,
#                 override_lob: str = None,
#                 override_segment: str = None) -> List[Dict]:
#         """
#         Process Excel sheet with structure:
#         Row 0: Title row (JAN 2025 PAYOUT - PC COMP)
#         Row 1: Main headers (Geo Locations | Payout on | Segment columns)
#         Row 2-3: Empty or sub-headers
#         Row 4+: Data rows
#         """
#         records = []
        
#         try:
#             # Read Excel without header to inspect structure
#             df = pd.read_excel(io.BytesIO(content), sheet_name=sheet_name, header=None)
            
#             print(f"\n[PROCESSOR] Processing sheet: {sheet_name}")
#             print(f"[PROCESSOR] Sheet shape: {df.shape}")
            
#             # Find the header row (contains "Geo Locations")
#             header_row = None
#             for i in range(min(10, df.shape[0])):
#                 row_text = " ".join(cell_to_str(v) for v in df.iloc[i]).upper()
#                 if "GEO LOCATION" in row_text or "GEO LOC" in row_text:
#                     header_row = i
#                     break
            
#             if header_row is None:
#                 print("[PROCESSOR] Could not find 'Geo Locations' header row")
#                 return records
            
#             print(f"[PROCESSOR] Found header row at index: {header_row}")
            
#             # The actual data starts after header row
#             data_start = header_row + 1
            
#             # Skip any empty rows after header
#             for i in range(data_start, df.shape[0]):
#                 if cell_to_str(df.iloc[i, 0]):  # First column has content
#                     data_start = i
#                     break
            
#             print(f"[PROCESSOR] Data starts at row: {data_start}")
            
#             # Build column metadata from header row
#             col_meta = []
#             for col_idx in range(2, df.shape[1]):  # Skip column 0 (Geo) and 1 (Payout on)
#                 header = cell_to_str(df.iloc[header_row, col_idx])
                
#                 if not header:
#                     continue
                
#                 # Determine policy type and segment from header
#                 header_upper = header.upper()
                
#                 if "COMP" in header_upper and "SOD" not in header_upper:
#                     policy_type = "COMP"
#                     segment = "PVT CAR COMP + SAOD"
#                 elif "SOD" in header_upper or "SAOD" in header_upper:
#                     policy_type = "SAOD"
#                     segment = "PVT CAR COMP + SAOD"
#                 elif "TP" in header_upper:
#                     policy_type = "TP"
#                     segment = "PVT CAR TP"
#                 else:
#                     policy_type = "COMP"
#                     segment = "PVT CAR COMP + SAOD"
                
#                 col_meta.append({
#                     "col_idx": col_idx,
#                     "header": header,
#                     "policy_type": policy_type,
#                     "segment": segment,
#                 })
            
#             if not col_meta:
#                 print("[PROCESSOR] No data columns found")
#                 return records
            
#             print(f"[PROCESSOR] Found {len(col_meta)} data columns")
#             for m in col_meta:
#                 print(f"  - Col {m['col_idx']}: {m['header']} -> {m['policy_type']}")
            
#             # Process data rows
#             lob_final = override_lob if override_enabled and override_lob else "PVT CAR"
            
#             skip_words = {"total", "grand total", "average", "sum", ""}
            
#             for row_idx in range(data_start, df.shape[0]):
#                 geo_location = cell_to_str(df.iloc[row_idx, 0])
                
#                 if not geo_location or geo_location.lower() in skip_words:
#                     continue
                
#                 state = map_state(geo_location)
                
#                 # Process each column
#                 for m in col_meta:
#                     payin = safe_float(df.iloc[row_idx, m["col_idx"]])
                    
#                     if payin is None or payin == 0:
#                         continue
                    
#                     segment_final = override_segment if override_enabled and override_segment else m["segment"]
                    
#                     payout, formula, explanation = calculate_payout(payin, lob_final, segment_final)
                    
#                     records.append({
#                         "State": state,
#                         "Geo Location": geo_location,
#                         "Original Segment": m["header"],
#                         "Mapped Segment": segment_final,
#                         "LOB": lob_final,
#                         "Policy Type": m["policy_type"],
#                         "Status": "STP",
#                         "Payin (OD Premium)": f"{payin:.2f}%",
#                         "Calculated Payout": f"{payout:.2f}%",
#                         "Formula Used": formula,
#                         "Rule Explanation": explanation,
#                     })
            
#             print(f"[PROCESSOR] Extracted {len(records)} records")
#             return records
            
#         except Exception as e:
#             print(f"[PROCESSOR] Error: {e}")
#             traceback.print_exc()
#             return []


# # ===============================================================================
# # API ENDPOINTS
# # ===============================================================================

# @app.get("/")
# async def root():
#     return {
#         "message": "Insurance Payout Processor API",
#         "version": "1.0.0",
#         "formula": "90% of Payin for all segments",
#         "supported_lobs": ["PVT CAR"],
#         "supported_segments": ["PVT CAR COMP + SAOD", "PVT CAR TP"]
#     }


# @app.post("/upload")
# async def upload_file(file: UploadFile = File(...)):
#     """Upload Excel file and return worksheet list."""
#     try:
#         if not file.filename.endswith((".xlsx", ".xls")):
#             raise HTTPException(status_code=400, detail="Only Excel files are supported")
        
#         content = await file.read()
#         xls = pd.ExcelFile(io.BytesIO(content))
#         sheets = xls.sheet_names
        
#         file_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
#         uploaded_files[file_id] = {
#             "content": content,
#             "filename": file.filename,
#             "sheets": sheets,
#         }
        
#         return {
#             "file_id": file_id,
#             "filename": file.filename,
#             "sheets": sheets,
#             "message": f"Uploaded successfully. {len(sheets)} worksheet(s) found.",
#         }
        
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Upload error: {str(e)}")


# @app.post("/process")
# async def process_sheet(
#     file_id: str,
#     sheet_name: str,
#     override_enabled: bool = False,
#     override_lob: Optional[str] = None,
#     override_segment: Optional[str] = None,
# ):
#     """Process a specific worksheet."""
#     try:
#         if file_id not in uploaded_files:
#             raise HTTPException(status_code=404, detail="File not found. Please re-upload.")
        
#         file_data = uploaded_files[file_id]
        
#         if sheet_name not in file_data["sheets"]:
#             raise HTTPException(status_code=400, detail=f"Sheet '{sheet_name}' not found")
        
#         records = ExcelProcessor.process(
#             file_data["content"], 
#             sheet_name,
#             override_enabled, 
#             override_lob, 
#             override_segment,
#         )
        
#         if not records:
#             return {
#                 "success": False,
#                 "message": "No records extracted. Check sheet structure.",
#                 "records": [],
#                 "count": 0,
#             }
        
#         # Calculate summary statistics
#         states = {}
#         policies = {}
#         payins = []
#         payouts = []
        
#         for r in records:
#             state = r.get("State", "UNKNOWN")
#             states[state] = states.get(state, 0) + 1
            
#             policy = r.get("Policy Type", "UNKNOWN")
#             policies[policy] = policies.get(policy, 0) + 1
            
#             try:
#                 payin_val = float(r.get("Payin (OD Premium)", "0%").replace("%", ""))
#                 payout_val = float(r.get("Calculated Payout", "0%").replace("%", ""))
#                 payins.append(payin_val)
#                 payouts.append(payout_val)
#             except Exception:
#                 pass
        
#         avg_payin = round(sum(payins) / len(payins), 2) if payins else 0
#         avg_payout = round(sum(payouts) / len(payouts), 2) if payouts else 0
        
#         return {
#             "success": True,
#             "message": f"Successfully processed {len(records)} records from '{sheet_name}'",
#             "records": records,
#             "count": len(records),
#             "summary": {
#                 "total_records": len(records),
#                 "states": dict(sorted(states.items(), key=lambda x: x[1], reverse=True)[:10]),
#                 "policy_types": policies,
#                 "average_payin": avg_payin,
#                 "average_payout": avg_payout,
#             },
#         }
        
#     except Exception as e:
#         traceback.print_exc()
#         raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")


# @app.post("/export")
# async def export_to_excel(file_id: str, sheet_name: str, records: List[Dict]):
#     """Export processed records to Excel."""
#     try:
#         if not records:
#             raise HTTPException(status_code=400, detail="No records to export")
        
#         df = pd.DataFrame(records)
        
#         timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#         filename = f"Processed_{sheet_name.replace(' ', '_')}_{timestamp}.xlsx"
#         out_path = os.path.join(tempfile.gettempdir(), filename)
        
#         # Create Excel writer with formatting
#         with pd.ExcelWriter(out_path, engine='openpyxl') as writer:
#             df.to_excel(writer, index=False, sheet_name="Processed Data")
            
#             # Auto-adjust column widths
#             worksheet = writer.sheets["Processed Data"]
#             for idx, col in enumerate(df.columns):
#                 max_length = max(
#                     df[col].astype(str).apply(len).max(),
#                     len(str(col))
#                 )
#                 worksheet.column_dimensions[chr(65 + idx)].width = min(max_length + 2, 50)
        
#         return FileResponse(
#             path=out_path,
#             filename=filename,
#             media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
#         )
        
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Export error: {str(e)}")


# @app.get("/health")
# async def health_check():
#     """Health check endpoint."""
#     return {
#         "status": "healthy",
#         "timestamp": datetime.now().isoformat(),
#         "uploaded_files": len(uploaded_files)
#     }


# if __name__ == "__main__":
#     import uvicorn
#     print("\n" + "=" * 70)
#     print("Insurance Payout Processor API - v1.0.0")
#     print("Formula: 90% of Payin for all PVT CAR segments")
#     print("=" * 70 + "\n")
#     uvicorn.run(app, host="0.0.0.0", port=8000)


# from fastapi import FastAPI, File, UploadFile, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import FileResponse, JSONResponse
# import pandas as pd
# import io
# import os
# from typing import List, Dict, Tuple, Optional
# from datetime import datetime
# import traceback
# import tempfile

# app = FastAPI(title="Insurance Payout Processor API")

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Update with your frontend URL
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # ===============================================================================
# # FORMULA DATA
# # ===============================================================================
# FORMULA_DATA = [
#     {"LOB": "PVT CAR", "SEGMENT": "PVT CAR COMP + SAOD", "PO": "90% of Payin", "REMARKS": "NIL"},
#     {"LOB": "PVT CAR", "SEGMENT": "PVT CAR TP", "PO": "90% of Payin", "REMARKS": "NIL"},
# ]

# # ===============================================================================
# # STATE MAPPING
# # ===============================================================================
# STATE_MAPPING = {
#     "ANDHRA PRADESH": "ANDHRA PRADESH",
#     "KRISHNA": "ANDHRA PRADESH",
#     "VIJAYWADA": "ANDHRA PRADESH",
#     "VIJAYAWADA": "ANDHRA PRADESH",
#     "VISAKHAPATNAM": "ANDHRA PRADESH",
#     "VIZAG": "ANDHRA PRADESH",
    
#     "KARNATAKA": "KARNATAKA",
#     "BANGALORE": "KARNATAKA",
#     "BENGALURU": "KARNATAKA",
#     "MYSORE": "KARNATAKA",
#     "MANGALORE": "KARNATAKA",
    
#     "KERALA": "KERALA",
#     "ERNAKULAM": "KERALA",
#     "COCHIN": "KERALA",
#     "KOCHI": "KERALA",
#     "TRIVANDRUM": "KERALA",
#     "CALICUT": "KERALA",
#     "KOZHIKODE": "KERALA",
    
#     "TAMIL NADU": "TAMIL NADU",
#     "CHENNAI": "TAMIL NADU",
#     "MADRAS": "TAMIL NADU",
#     "PONDICHERRY": "TAMIL NADU",
#     "PUDUCHERRY": "TAMIL NADU",
#     "COIMBATORE": "TAMIL NADU",
#     "MADURAI": "TAMIL NADU",
    
#     "TELANGANA": "TELANGANA",
#     "HYDERABAD": "TELANGANA",
#     "SECUNDERABAD": "TELANGANA",
    
#     "MAHARASHTRA": "MAHARASHTRA",
#     "MUMBAI": "MAHARASHTRA",
#     "PUNE": "MAHARASHTRA",
#     "NAGPUR": "MAHARASHTRA",
#     "THANE": "MAHARASHTRA",
#     "NASHIK": "MAHARASHTRA",
    
#     "DELHI": "DELHI",
#     "NEW DELHI": "DELHI",
#     "NCR": "DELHI",
    
#     "GUJARAT": "GUJARAT",
#     "AHMEDABAD": "GUJARAT",
#     "SURAT": "GUJARAT",
#     "VADODARA": "GUJARAT",
#     "RAJKOT": "GUJARAT",
    
#     "RAJASTHAN": "RAJASTHAN",
#     "JAIPUR": "RAJASTHAN",
#     "JODHPUR": "RAJASTHAN",
#     "UDAIPUR": "RAJASTHAN",
    
#     "UTTAR PRADESH": "UTTAR PRADESH",
#     "LUCKNOW": "UTTAR PRADESH",
#     "KANPUR": "UTTAR PRADESH",
#     "AGRA": "UTTAR PRADESH",
#     "VARANASI": "UTTAR PRADESH",
#     "NOIDA": "UTTAR PRADESH",
    
#     "WEST BENGAL": "WEST BENGAL",
#     "KOLKATA": "WEST BENGAL",
#     "CALCUTTA": "WEST BENGAL",
    
#     "MADHYA PRADESH": "MADHYA PRADESH",
#     "BHOPAL": "MADHYA PRADESH",
#     "INDORE": "MADHYA PRADESH",
    
#     "PUNJAB": "PUNJAB",
#     "CHANDIGARH": "CHANDIGARH",
#     "HARYANA": "HARYANA",
#     "GOA": "GOA",
#     "BIHAR": "BIHAR",
#     "PATNA": "BIHAR",
#     "JHARKHAND": "JHARKHAND",
#     "RANCHI": "JHARKHAND",
#     "ODISHA": "ODISHA",
#     "BHUBANESWAR": "ODISHA",
#     "ASSAM": "ASSAM",
#     "GUWAHATI": "ASSAM",
# }

# uploaded_files = {}

# # ===============================================================================
# # HELPER FUNCTIONS
# # ===============================================================================

# def cell_to_str(val) -> str:
#     """Safely convert ANY cell value (float NaN, None, int, str) to string."""
#     if val is None:
#         return ""
#     try:
#         if pd.isna(val):
#             return ""
#     except (TypeError, ValueError):
#         pass
#     return str(val).strip()


# def safe_float(value) -> Optional[float]:
#     """Safely convert value to float, handling percentages and invalid values."""
#     if value is None:
#         return None
#     try:
#         if pd.isna(value):
#             return None
#     except (TypeError, ValueError):
#         pass
    
#     s = str(value).strip().upper().replace("%", "")
#     if s in ["D", "NA", "", "NAN", "NONE", "DECLINE", "0.00%", "0.0%", "0%"]:
#         return None
    
#     try:
#         num = float(s)
#         if num < 0:
#             return None
#         # Convert decimals to percentages (0.28 -> 28%)
#         return num * 100 if 0 < num < 1 else num
#     except Exception:
#         return None


# def map_state(location: str) -> str:
#     """Map location/geo name to state using STATE_MAPPING."""
#     location_upper = location.upper()
    
#     # Direct match first
#     for key, val in STATE_MAPPING.items():
#         if key.upper() == location_upper:
#             return val
    
#     # Partial match
#     for key, val in STATE_MAPPING.items():
#         if key.upper() in location_upper:
#             return val
    
#     return location  # Return original if no match


# def calculate_payout(payin: float, lob: str = "PVT CAR", segment: str = "PVT CAR COMP + SAOD") -> Tuple[float, str, str]:
#     """
#     Calculate payout based on formula: 90% of Payin
#     """
#     if payin == 0 or payin is None:
#         return 0, "0% (No Payin)", "Payin is 0"
    
#     # Formula: 90% of Payin
#     payout = round(payin * 0.90, 2)
#     formula = "90% of Payin"
#     explanation = f"Applied formula: {formula} for {segment}"
    
#     return payout, formula, explanation


# # ===============================================================================
# # PATTERN DETECTION
# # ===============================================================================

# class PatternDetector:
#     """Detect the pattern type of the Excel sheet."""
    
#     @staticmethod
#     def detect_pattern(df: pd.DataFrame) -> str:
#         """
#         Detect pattern type:
#         - 'comp_saod': COMP/SAOD pattern (Comp - Petrol, SOD - NCB, etc.)
#         - 'satp_cc': SATP with CC bands (<1000 cc, 1000-1500 cc, >1500 cc)
#         """
#         # Check first 10 rows for pattern indicators
#         sample_text = ""
#         for i in range(min(10, df.shape[0])):
#             row_text = " ".join(cell_to_str(v) for v in df.iloc[i]).upper()
#             sample_text += row_text + " "
        
#         # SATP CC Band pattern detection
#         if ("SATP" in sample_text or "SA TP" in sample_text) and ("CC" in sample_text or "1000" in sample_text):
#             return "satp_cc"
        
#         # COMP/SAOD pattern (default)
#         return "comp_saod"


# # ===============================================================================
# # SATP CC BAND PROCESSOR
# # ===============================================================================

# class SATPCCProcessor:
#     """Process SATP (Third Party) sheets with CC (Cubic Capacity) bands."""
    
#     @staticmethod
#     def process(content: bytes, sheet_name: str,
#                 override_enabled: bool = False,
#                 override_lob: str = None,
#                 override_segment: str = None) -> List[Dict]:
#         """
#         Process SATP CC Band pattern:
#         Row 1: Title (JAN 2025 PAYOUT - PC TP)
#         Row 2: Geo Locations | SATP Petrol | SATP Diesel
#         Row 3: (empty) | <1000 cc | 1000-1500 cc | >1500 cc | 1000-1500 cc | >1500 cc
#         Row 4+: Data rows
#         """
#         records = []
        
#         try:
#             df = pd.read_excel(io.BytesIO(content), sheet_name=sheet_name, header=None)
            
#             print(f"\n[SATP_CC] Processing sheet: {sheet_name}")
#             print(f"[SATP_CC] Sheet shape: {df.shape}")
            
#             # Find the "Geo Locations" header row
#             header_row = None
#             for i in range(min(10, df.shape[0])):
#                 row_text = cell_to_str(df.iloc[i, 0]).upper()
#                 if "GEO LOCATION" in row_text or "GEO LOC" in row_text:
#                     header_row = i
#                     break
            
#             if header_row is None:
#                 print("[SATP_CC] 'Geo Locations' header row not found")
#                 return records
            
#             print(f"[SATP_CC] Found header row at index: {header_row}")
            
#             # Row structure:
#             # header_row: Geo Locations | SATP Petrol | SATP Diesel
#             # header_row + 1: (empty) | <1000 cc | 1000-1500 cc | >1500 cc | ...
#             cc_row = header_row + 1
            
#             # Data starts after CC row
#             data_start = cc_row + 1
            
#             # Skip empty rows
#             for i in range(data_start, df.shape[0]):
#                 if cell_to_str(df.iloc[i, 0]):
#                     data_start = i
#                     break
            
#             print(f"[SATP_CC] CC row: {cc_row}, Data starts: {data_start}")
            
#             # Build column metadata
#             col_meta = []
#             for col_idx in range(1, df.shape[1]):
#                 fuel_type = cell_to_str(df.iloc[header_row, col_idx]).upper()
#                 cc_band = cell_to_str(df.iloc[cc_row, col_idx])
                
#                 if not fuel_type and not cc_band:
#                     continue
                
#                 # Determine fuel type from header
#                 if "PETROL" in fuel_type:
#                     fuel = "Petrol"
#                 elif "DIESEL" in fuel_type:
#                     fuel = "Diesel"
#                 else:
#                     # Use previous fuel type (for merged cells)
#                     if col_meta:
#                         fuel = col_meta[-1]["fuel_type"]
#                     else:
#                         fuel = "Unknown"
                
#                 # Build segment description
#                 segment_desc = f"SATP {fuel}"
#                 if cc_band:
#                     segment_desc += f" ({cc_band})"
                
#                 col_meta.append({
#                     "col_idx": col_idx,
#                     "fuel_type": fuel,
#                     "cc_band": cc_band,
#                     "segment_desc": segment_desc,
#                 })
            
#             if not col_meta:
#                 print("[SATP_CC] No data columns found")
#                 return records
            
#             print(f"[SATP_CC] Found {len(col_meta)} columns")
#             for m in col_meta:
#                 print(f"  - Col {m['col_idx']}: {m['segment_desc']}")
            
#             # Process data rows
#             lob_final = override_lob if override_enabled and override_lob else "PVT CAR"
#             segment_final = override_segment if override_enabled and override_segment else "PVT CAR TP"
            
#             skip_words = {"total", "grand total", "average", "sum", ""}
            
#             for row_idx in range(data_start, df.shape[0]):
#                 geo_location = cell_to_str(df.iloc[row_idx, 0])
                
#                 if not geo_location or geo_location.lower() in skip_words:
#                     continue
                
#                 state = map_state(geo_location)
                
#                 # Process each column
#                 for m in col_meta:
#                     payin = safe_float(df.iloc[row_idx, m["col_idx"]])
                    
#                     if payin is None or payin == 0:
#                         continue
                    
#                     payout, formula, explanation = calculate_payout(payin, lob_final, segment_final)
                    
#                     records.append({
#                         "State": state,
#                         "Geo Location": geo_location,
#                         "Original Segment": m["segment_desc"],
#                         "Mapped Segment": segment_final,
#                         "LOB": lob_final,
#                         "Policy Type": "TP",
#                         "Status": "STP",
#                         "Payin (OD Premium)": f"{payin:.2f}%",
#                         "Calculated Payout": f"{payout:.2f}%",
#                         "Formula Used": formula,
#                         "Rule Explanation": explanation,
#                         "Fuel Type": m["fuel_type"],
#                         "CC Band": m["cc_band"],
#                     })
            
#             print(f"[SATP_CC] Extracted {len(records)} records")
#             return records
            
#         except Exception as e:
#             print(f"[SATP_CC] Error: {e}")
#             traceback.print_exc()
#             return []


# # ===============================================================================
# # COMP/SAOD PROCESSOR (Original Pattern)
# # ===============================================================================

# class CompSaodProcessor:
#     """Process COMP/SAOD pattern sheets."""
    
#     @staticmethod
#     def process(content: bytes, sheet_name: str,
#                 override_enabled: bool = False,
#                 override_lob: str = None,
#                 override_segment: str = None) -> List[Dict]:
#         """
#         Process Excel sheet with structure:
#         Row 0: Title row (JAN 2025 PAYOUT - PC COMP)
#         Row 1: Main headers (Geo Locations | Payout on | Segment columns)
#         Row 2-3: Empty or sub-headers
#         Row 4+: Data rows
#         """
#         records = []
        
#         try:
#             # Read Excel without header to inspect structure
#             df = pd.read_excel(io.BytesIO(content), sheet_name=sheet_name, header=None)
            
#             print(f"\n[COMP_SAOD] Processing sheet: {sheet_name}")
#             print(f"[COMP_SAOD] Sheet shape: {df.shape}")
            
#             # Find the header row (contains "Geo Locations")
#             header_row = None
#             for i in range(min(10, df.shape[0])):
#                 row_text = " ".join(cell_to_str(v) for v in df.iloc[i]).upper()
#                 if "GEO LOCATION" in row_text or "GEO LOC" in row_text:
#                     header_row = i
#                     break
            
#             if header_row is None:
#                 print("[COMP_SAOD] Could not find 'Geo Locations' header row")
#                 return records
            
#             print(f"[COMP_SAOD] Found header row at index: {header_row}")
            
#             # The actual data starts after header row
#             data_start = header_row + 1
            
#             # Skip any empty rows after header
#             for i in range(data_start, df.shape[0]):
#                 if cell_to_str(df.iloc[i, 0]):  # First column has content
#                     data_start = i
#                     break
            
#             print(f"[COMP_SAOD] Data starts at row: {data_start}")
            
#             # Build column metadata from header row
#             col_meta = []
#             for col_idx in range(2, df.shape[1]):  # Skip column 0 (Geo) and 1 (Payout on)
#                 header = cell_to_str(df.iloc[header_row, col_idx])
                
#                 if not header:
#                     continue
                
#                 # Determine policy type and segment from header
#                 header_upper = header.upper()
                
#                 if "COMP" in header_upper and "SOD" not in header_upper:
#                     policy_type = "COMP"
#                     segment = "PVT CAR COMP + SAOD"
#                 elif "SOD" in header_upper or "SAOD" in header_upper:
#                     policy_type = "SAOD"
#                     segment = "PVT CAR COMP + SAOD"
#                 elif "TP" in header_upper:
#                     policy_type = "TP"
#                     segment = "PVT CAR TP"
#                 else:
#                     policy_type = "COMP"
#                     segment = "PVT CAR COMP + SAOD"
                
#                 col_meta.append({
#                     "col_idx": col_idx,
#                     "header": header,
#                     "policy_type": policy_type,
#                     "segment": segment,
#                 })
            
#             if not col_meta:
#                 print("[COMP_SAOD] No data columns found")
#                 return records
            
#             print(f"[COMP_SAOD] Found {len(col_meta)} data columns")
#             for m in col_meta:
#                 print(f"  - Col {m['col_idx']}: {m['header']} -> {m['policy_type']}")
            
#             # Process data rows
#             lob_final = override_lob if override_enabled and override_lob else "PVT CAR"
            
#             skip_words = {"total", "grand total", "average", "sum", ""}
            
#             for row_idx in range(data_start, df.shape[0]):
#                 geo_location = cell_to_str(df.iloc[row_idx, 0])
                
#                 if not geo_location or geo_location.lower() in skip_words:
#                     continue
                
#                 state = map_state(geo_location)
                
#                 # Process each column
#                 for m in col_meta:
#                     payin = safe_float(df.iloc[row_idx, m["col_idx"]])
                    
#                     if payin is None or payin == 0:
#                         continue
                    
#                     segment_final = override_segment if override_enabled and override_segment else m["segment"]
                    
#                     payout, formula, explanation = calculate_payout(payin, lob_final, segment_final)
                    
#                     records.append({
#                         "State": state,
#                         "Geo Location": geo_location,
#                         "Original Segment": m["header"],
#                         "Mapped Segment": segment_final,
#                         "LOB": lob_final,
#                         "Policy Type": m["policy_type"],
#                         "Status": "STP",
#                         "Payin (OD Premium)": f"{payin:.2f}%",
#                         "Calculated Payout": f"{payout:.2f}%",
#                         "Formula Used": formula,
#                         "Rule Explanation": explanation,
#                     })
            
#             print(f"[COMP_SAOD] Extracted {len(records)} records")
#             return records
            
#         except Exception as e:
#             print(f"[COMP_SAOD] Error: {e}")
#             traceback.print_exc()
#             return []


# # ===============================================================================
# # PATTERN DISPATCHER
# # ===============================================================================

# class PatternDispatcher:
#     """Route to the correct processor based on detected pattern."""
    
#     PATTERN_PROCESSORS = {
#         "comp_saod": CompSaodProcessor,
#         "satp_cc": SATPCCProcessor,
#     }
    
#     @staticmethod
#     def process_sheet(content: bytes, sheet_name: str,
#                       override_enabled: bool = False,
#                       override_lob: str = None,
#                       override_segment: str = None) -> List[Dict]:
#         """Detect pattern and route to appropriate processor."""
#         # Read raw data to detect pattern
#         df_raw = pd.read_excel(io.BytesIO(content), sheet_name=sheet_name, header=None)
#         pattern = PatternDetector.detect_pattern(df_raw)
        
#         print(f"\n[DISPATCHER] Detected pattern: {pattern}")
        
#         processor_class = PatternDispatcher.PATTERN_PROCESSORS.get(pattern, CompSaodProcessor)
#         return processor_class.process(
#             content, sheet_name,
#             override_enabled, override_lob, override_segment
#         )
#         """
#         Process Excel sheet with structure:
#         Row 0: Title row (JAN 2025 PAYOUT - PC COMP)
#         Row 1: Main headers (Geo Locations | Payout on | Segment columns)
#         Row 2-3: Empty or sub-headers
#         Row 4+: Data rows
#         """
#         records = []
        
#         try:
#             # Read Excel without header to inspect structure
#             df = pd.read_excel(io.BytesIO(content), sheet_name=sheet_name, header=None)
            
#             print(f"\n[PROCESSOR] Processing sheet: {sheet_name}")
#             print(f"[PROCESSOR] Sheet shape: {df.shape}")
            
#             # Find the header row (contains "Geo Locations")
#             header_row = None
#             for i in range(min(10, df.shape[0])):
#                 row_text = " ".join(cell_to_str(v) for v in df.iloc[i]).upper()
#                 if "GEO LOCATION" in row_text or "GEO LOC" in row_text:
#                     header_row = i
#                     break
            
#             if header_row is None:
#                 print("[PROCESSOR] Could not find 'Geo Locations' header row")
#                 return records
            
#             print(f"[PROCESSOR] Found header row at index: {header_row}")
            
#             # The actual data starts after header row
#             data_start = header_row + 1
            
#             # Skip any empty rows after header
#             for i in range(data_start, df.shape[0]):
#                 if cell_to_str(df.iloc[i, 0]):  # First column has content
#                     data_start = i
#                     break
            
#             print(f"[PROCESSOR] Data starts at row: {data_start}")
            
#             # Build column metadata from header row
#             col_meta = []
#             for col_idx in range(2, df.shape[1]):  # Skip column 0 (Geo) and 1 (Payout on)
#                 header = cell_to_str(df.iloc[header_row, col_idx])
                
#                 if not header:
#                     continue
                
#                 # Determine policy type and segment from header
#                 header_upper = header.upper()
                
#                 if "COMP" in header_upper and "SOD" not in header_upper:
#                     policy_type = "COMP"
#                     segment = "PVT CAR COMP + SAOD"
#                 elif "SOD" in header_upper or "SAOD" in header_upper:
#                     policy_type = "SAOD"
#                     segment = "PVT CAR COMP + SAOD"
#                 elif "TP" in header_upper:
#                     policy_type = "TP"
#                     segment = "PVT CAR TP"
#                 else:
#                     policy_type = "COMP"
#                     segment = "PVT CAR COMP + SAOD"
                
#                 col_meta.append({
#                     "col_idx": col_idx,
#                     "header": header,
#                     "policy_type": policy_type,
#                     "segment": segment,
#                 })
            
#             if not col_meta:
#                 print("[PROCESSOR] No data columns found")
#                 return records
            
#             print(f"[PROCESSOR] Found {len(col_meta)} data columns")
#             for m in col_meta:
#                 print(f"  - Col {m['col_idx']}: {m['header']} -> {m['policy_type']}")
            
#             # Process data rows
#             lob_final = override_lob if override_enabled and override_lob else "PVT CAR"
            
#             skip_words = {"total", "grand total", "average", "sum", ""}
            
#             for row_idx in range(data_start, df.shape[0]):
#                 geo_location = cell_to_str(df.iloc[row_idx, 0])
                
#                 if not geo_location or geo_location.lower() in skip_words:
#                     continue
                
#                 state = map_state(geo_location)
                
#                 # Process each column
#                 for m in col_meta:
#                     payin = safe_float(df.iloc[row_idx, m["col_idx"]])
                    
#                     if payin is None or payin == 0:
#                         continue
                    
#                     segment_final = override_segment if override_enabled and override_segment else m["segment"]
                    
#                     payout, formula, explanation = calculate_payout(payin, lob_final, segment_final)
                    
#                     records.append({
#                         "State": state,
#                         "Geo Location": geo_location,
#                         "Original Segment": m["header"],
#                         "Mapped Segment": segment_final,
#                         "LOB": lob_final,
#                         "Policy Type": m["policy_type"],
#                         "Status": "STP",
#                         "Payin (OD Premium)": f"{payin:.2f}%",
#                         "Calculated Payout": f"{payout:.2f}%",
#                         "Formula Used": formula,
#                         "Rule Explanation": explanation,
#                     })
            
#             print(f"[PROCESSOR] Extracted {len(records)} records")
#             return records
            
#         except Exception as e:
#             print(f"[PROCESSOR] Error: {e}")
#             traceback.print_exc()
#             return []


# # ===============================================================================
# # API ENDPOINTS
# # ===============================================================================

# @app.get("/")
# async def root():
#     return {
#         "message": "Insurance Payout Processor API",
#         "version": "2.0.0",
#         "formula": "90% of Payin for all segments",
#         "supported_lobs": ["PVT CAR"],
#         "supported_segments": ["PVT CAR COMP + SAOD", "PVT CAR TP"],
#         "supported_patterns": [
#             "comp_saod - COMP/SAOD with fuel types (Petrol, Diesel, NCB variants)",
#             "satp_cc - SATP (Third Party) with CC bands (<1000cc, 1000-1500cc, >1500cc)"
#         ]
#     }


# @app.post("/upload")
# async def upload_file(file: UploadFile = File(...)):
#     """Upload Excel file and return worksheet list."""
#     try:
#         if not file.filename.endswith((".xlsx", ".xls")):
#             raise HTTPException(status_code=400, detail="Only Excel files are supported")
        
#         content = await file.read()
#         xls = pd.ExcelFile(io.BytesIO(content))
#         sheets = xls.sheet_names
        
#         file_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
#         uploaded_files[file_id] = {
#             "content": content,
#             "filename": file.filename,
#             "sheets": sheets,
#         }
        
#         return {
#             "file_id": file_id,
#             "filename": file.filename,
#             "sheets": sheets,
#             "message": f"Uploaded successfully. {len(sheets)} worksheet(s) found.",
#         }
        
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Upload error: {str(e)}")


# @app.post("/process")
# async def process_sheet(
#     file_id: str,
#     sheet_name: str,
#     override_enabled: bool = False,
#     override_lob: Optional[str] = None,
#     override_segment: Optional[str] = None,
# ):
#     """Process a specific worksheet."""
#     try:
#         if file_id not in uploaded_files:
#             raise HTTPException(status_code=404, detail="File not found. Please re-upload.")
        
#         file_data = uploaded_files[file_id]
        
#         if sheet_name not in file_data["sheets"]:
#             raise HTTPException(status_code=400, detail=f"Sheet '{sheet_name}' not found")
        
#         # Use PatternDispatcher to automatically detect and process
#         records = PatternDispatcher.process_sheet(
#             file_data["content"], 
#             sheet_name,
#             override_enabled, 
#             override_lob, 
#             override_segment,
#         )
        
#         if not records:
#             return {
#                 "success": False,
#                 "message": "No records extracted. Check sheet structure.",
#                 "records": [],
#                 "count": 0,
#             }
        
#         # Calculate summary statistics
#         states = {}
#         policies = {}
#         payins = []
#         payouts = []
        
#         for r in records:
#             state = r.get("State", "UNKNOWN")
#             states[state] = states.get(state, 0) + 1
            
#             policy = r.get("Policy Type", "UNKNOWN")
#             policies[policy] = policies.get(policy, 0) + 1
            
#             try:
#                 payin_val = float(r.get("Payin (OD Premium)", "0%").replace("%", ""))
#                 payout_val = float(r.get("Calculated Payout", "0%").replace("%", ""))
#                 payins.append(payin_val)
#                 payouts.append(payout_val)
#             except Exception:
#                 pass
        
#         avg_payin = round(sum(payins) / len(payins), 2) if payins else 0
#         avg_payout = round(sum(payouts) / len(payouts), 2) if payouts else 0
        
#         return {
#             "success": True,
#             "message": f"Successfully processed {len(records)} records from '{sheet_name}'",
#             "records": records,
#             "count": len(records),
#             "summary": {
#                 "total_records": len(records),
#                 "states": dict(sorted(states.items(), key=lambda x: x[1], reverse=True)[:10]),
#                 "policy_types": policies,
#                 "average_payin": avg_payin,
#                 "average_payout": avg_payout,
#             },
#         }
        
#     except Exception as e:
#         traceback.print_exc()
#         raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")


# @app.post("/export")
# async def export_to_excel(file_id: str, sheet_name: str, records: List[Dict]):
#     """Export processed records to Excel."""
#     try:
#         if not records:
#             raise HTTPException(status_code=400, detail="No records to export")
        
#         df = pd.DataFrame(records)
        
#         timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#         filename = f"Processed_{sheet_name.replace(' ', '_')}_{timestamp}.xlsx"
#         out_path = os.path.join(tempfile.gettempdir(), filename)
        
#         # Create Excel writer with formatting
#         with pd.ExcelWriter(out_path, engine='openpyxl') as writer:
#             df.to_excel(writer, index=False, sheet_name="Processed Data")
            
#             # Auto-adjust column widths
#             worksheet = writer.sheets["Processed Data"]
#             for idx, col in enumerate(df.columns):
#                 max_length = max(
#                     df[col].astype(str).apply(len).max(),
#                     len(str(col))
#                 )
#                 worksheet.column_dimensions[chr(65 + idx)].width = min(max_length + 2, 50)
        
#         return FileResponse(
#             path=out_path,
#             filename=filename,
#             media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
#         )
        
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Export error: {str(e)}")


# @app.get("/health")
# async def health_check():
#     """Health check endpoint."""
#     return {
#         "status": "healthy",
#         "timestamp": datetime.now().isoformat(),
#         "uploaded_files": len(uploaded_files)
#     }


# if __name__ == "__main__":
#     import uvicorn
#     print("\n" + "=" * 70)
#     print("Insurance Payout Processor API - v2.0.0")
#     print("Formula: 90% of Payin for all PVT CAR segments")
#     print("Patterns: COMP/SAOD + SATP with CC bands")
#     print("=" * 70 + "\n")
#     uvicorn.run(app, host="0.0.0.0", port=8000)



# from fastapi import FastAPI, File, UploadFile, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import FileResponse, JSONResponse
# import pandas as pd
# import io
# import os
# from typing import List, Dict, Tuple, Optional
# from datetime import datetime
# import traceback
# import tempfile

# app = FastAPI(title="Insurance Payout Processor API")

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Update with your frontend URL
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # ===============================================================================
# # FORMULA DATA
# # ===============================================================================
# FORMULA_DATA = [
#     {"LOB": "PVT CAR", "SEGMENT": "PVT CAR COMP + SAOD", "PO": "90% of Payin", "REMARKS": "NIL"},
#     {"LOB": "PVT CAR", "SEGMENT": "PVT CAR TP", "PO": "90% of Payin", "REMARKS": "NIL"},
# ]

# # ===============================================================================
# # STATE MAPPING
# # ===============================================================================
# STATE_MAPPING = {
#     "ANDHRA PRADESH": "ANDHRA PRADESH",
#     "KRISHNA": "ANDHRA PRADESH",
#     "VIJAYWADA": "ANDHRA PRADESH",
#     "VIJAYAWADA": "ANDHRA PRADESH",
#     "VISAKHAPATNAM": "ANDHRA PRADESH",
#     "VIZAG": "ANDHRA PRADESH",
    
#     "KARNATAKA": "KARNATAKA",
#     "BANGALORE": "KARNATAKA",
#     "BENGALURU": "KARNATAKA",
#     "MYSORE": "KARNATAKA",
#     "MANGALORE": "KARNATAKA",
    
#     "KERALA": "KERALA",
#     "ERNAKULAM": "KERALA",
#     "COCHIN": "KERALA",
#     "KOCHI": "KERALA",
#     "TRIVANDRUM": "KERALA",
#     "CALICUT": "KERALA",
#     "KOZHIKODE": "KERALA",
    
#     "TAMIL NADU": "TAMIL NADU",
#     "CHENNAI": "TAMIL NADU",
#     "MADRAS": "TAMIL NADU",
#     "PONDICHERRY": "TAMIL NADU",
#     "PUDUCHERRY": "TAMIL NADU",
#     "COIMBATORE": "TAMIL NADU",
#     "MADURAI": "TAMIL NADU",
    
#     "TELANGANA": "TELANGANA",
#     "HYDERABAD": "TELANGANA",
#     "SECUNDERABAD": "TELANGANA",
    
#     "MAHARASHTRA": "MAHARASHTRA",
#     "MUMBAI": "MAHARASHTRA",
#     "PUNE": "MAHARASHTRA",
#     "NAGPUR": "MAHARASHTRA",
#     "THANE": "MAHARASHTRA",
#     "NASHIK": "MAHARASHTRA",
    
#     "DELHI": "DELHI",
#     "NEW DELHI": "DELHI",
#     "NCR": "DELHI",
    
#     "GUJARAT": "GUJARAT",
#     "AHMEDABAD": "GUJARAT",
#     "SURAT": "GUJARAT",
#     "VADODARA": "GUJARAT",
#     "RAJKOT": "GUJARAT",
    
#     "RAJASTHAN": "RAJASTHAN",
#     "JAIPUR": "RAJASTHAN",
#     "JODHPUR": "RAJASTHAN",
#     "UDAIPUR": "RAJASTHAN",
    
#     "UTTAR PRADESH": "UTTAR PRADESH",
#     "LUCKNOW": "UTTAR PRADESH",
#     "KANPUR": "UTTAR PRADESH",
#     "AGRA": "UTTAR PRADESH",
#     "VARANASI": "UTTAR PRADESH",
#     "NOIDA": "UTTAR PRADESH",
    
#     "WEST BENGAL": "WEST BENGAL",
#     "KOLKATA": "WEST BENGAL",
#     "CALCUTTA": "WEST BENGAL",
    
#     "MADHYA PRADESH": "MADHYA PRADESH",
#     "BHOPAL": "MADHYA PRADESH",
#     "INDORE": "MADHYA PRADESH",
    
#     "PUNJAB": "PUNJAB",
#     "CHANDIGARH": "CHANDIGARH",
#     "HARYANA": "HARYANA",
#     "GOA": "GOA",
#     "BIHAR": "BIHAR",
#     "PATNA": "BIHAR",
#     "JHARKHAND": "JHARKHAND",
#     "RANCHI": "JHARKHAND",
#     "ODISHA": "ODISHA",
#     "BHUBANESWAR": "ODISHA",
#     "ASSAM": "ASSAM",
#     "GUWAHATI": "ASSAM",
# }

# uploaded_files = {}

# # ===============================================================================
# # HELPER FUNCTIONS
# # ===============================================================================

# def cell_to_str(val) -> str:
#     """Safely convert ANY cell value (float NaN, None, int, str) to string."""
#     if val is None:
#         return ""
#     try:
#         if pd.isna(val):
#             return ""
#     except (TypeError, ValueError):
#         pass
#     return str(val).strip()


# def safe_float(value) -> Optional[float]:
#     """Safely convert value to float, handling percentages and invalid values."""
#     if value is None:
#         return None
#     try:
#         if pd.isna(value):
#             return None
#     except (TypeError, ValueError):
#         pass
    
#     s = str(value).strip().upper().replace("%", "")
#     if s in ["D", "NA", "", "NAN", "NONE", "DECLINE", "0.00%", "0.0%", "0%"]:
#         return None
    
#     try:
#         num = float(s)
#         if num < 0:
#             return None
#         # Convert decimals to percentages (0.28 -> 28%)
#         return num * 100 if 0 < num < 1 else num
#     except Exception:
#         return None


# def map_state(location: str) -> str:
#     """Map location/geo name to state using STATE_MAPPING."""
#     location_upper = location.upper()
    
#     # Direct match first
#     for key, val in STATE_MAPPING.items():
#         if key.upper() == location_upper:
#             return val
    
#     # Partial match
#     for key, val in STATE_MAPPING.items():
#         if key.upper() in location_upper:
#             return val
    
#     return location  # Return original if no match


# def calculate_payout(payin: float, lob: str = "PVT CAR", segment: str = "PVT CAR COMP + SAOD") -> Tuple[float, str, str]:
#     """
#     Calculate payout based on formula: 90% of Payin
#     """
#     if payin == 0 or payin is None:
#         return 0, "0% (No Payin)", "Payin is 0"
    
#     # Formula: 90% of Payin
#     payout = round(payin * 0.90, 2)
#     formula = "90% of Payin"
#     explanation = f"Applied formula: {formula} for {segment}"
    
#     return payout, formula, explanation


# # ===============================================================================
# # PATTERN DETECTION
# # ===============================================================================

# class PatternDetector:
#     """Detect the pattern type of the Excel sheet."""
    
#     @staticmethod
#     def detect_pattern(df: pd.DataFrame) -> str:
#         """
#         Detect pattern type:
#         - 'comp_saod': COMP/SAOD pattern (Comp - Petrol, SOD - NCB, etc.)
#         - 'satp_cc': SATP with CC bands (<1000 cc, 1000-1500 cc, >1500 cc)
#         - 'geo_new_old_comp': COMP pattern with Geo segment New/Old columns
#         - 'geo_new_old_satp': SATP pattern with Geo segment New/Old columns
#         """
#         # Check first 10 rows for pattern indicators
#         sample_text = ""
#         for i in range(min(10, df.shape[0])):
#             row_text = " ".join(cell_to_str(v) for v in df.iloc[i]).upper()
#             sample_text += row_text + " "
        
#         # Check for Geo segment New/Old pattern
#         has_geo_new = "GEO SEGMENT NEW" in sample_text or "GEO SEGMENT OLD" in sample_text
        
#         if has_geo_new:
#             # Determine if it's COMP or SATP
#             if "PCCOMP" in sample_text or "PC COMP" in sample_text or "PAYOUT - PCCOMP" in sample_text:
#                 return "geo_new_old_comp"
#             elif "PCSATP" in sample_text or "PC SATP" in sample_text or "SATP" in sample_text:
#                 return "geo_new_old_satp"
        
#         # SATP CC Band pattern detection
#         if ("SATP" in sample_text or "SA TP" in sample_text) and ("CC" in sample_text or "1000" in sample_text):
#             return "satp_cc"
        
#         # COMP/SAOD pattern (default)
#         return "comp_saod"


# # ===============================================================================
# # GEO NEW/OLD COMP PROCESSOR
# # ===============================================================================

# class GeoNewOldCompProcessor:
#     """Process COMP sheets with Geo segment New and Geo segment Old columns."""
    
#     @staticmethod
#     def process(content: bytes, sheet_name: str,
#                 override_enabled: bool = False,
#                 override_lob: str = None,
#                 override_segment: str = None) -> List[Dict]:
#         """
#         Process pattern:
#         Row 1: Title (March 2025 PAYOUT - PCCOMP)
#         Row 2: Empty
#         Row 3: Geo segment New | Geo segment Old | Comp - Petrol - NCB / NON NCB | ...
#         Row 4+: Data rows
#         """
#         records = []
        
#         try:
#             df = pd.read_excel(io.BytesIO(content), sheet_name=sheet_name, header=None)
            
#             print(f"\n[GEO_NEW_OLD_COMP] Processing sheet: {sheet_name}")
#             print(f"[GEO_NEW_OLD_COMP] Sheet shape: {df.shape}")
            
#             # Find header row with "Geo segment New"
#             header_row = None
#             for i in range(min(10, df.shape[0])):
#                 row_text = " ".join(cell_to_str(v) for v in df.iloc[i]).upper()
#                 if "GEO SEGMENT NEW" in row_text:
#                     header_row = i
#                     break
            
#             if header_row is None:
#                 print("[GEO_NEW_OLD_COMP] Header row not found")
#                 return records
            
#             print(f"[GEO_NEW_OLD_COMP] Found header row at index: {header_row}")
            
#             # Data starts after header
#             data_start = header_row + 1
            
#             # Build column metadata (starting from column 2, after Geo New and Geo Old)
#             col_meta = []
#             for col_idx in range(2, df.shape[1]):
#                 header = cell_to_str(df.iloc[header_row, col_idx])
                
#                 if not header:
#                     continue
                
#                 header_upper = header.upper()
                
#                 # Determine policy type
#                 if "COMP" in header_upper and "SOD" not in header_upper and "SAOD" not in header_upper:
#                     policy_type = "COMP"
#                 elif "SOD" in header_upper or "SAOD" in header_upper:
#                     policy_type = "SAOD"
#                 else:
#                     policy_type = "COMP"
                
#                 col_meta.append({
#                     "col_idx": col_idx,
#                     "header": header,
#                     "policy_type": policy_type,
#                 })
            
#             if not col_meta:
#                 print("[GEO_NEW_OLD_COMP] No data columns found")
#                 return records
            
#             print(f"[GEO_NEW_OLD_COMP] Found {len(col_meta)} columns")
            
#             # Process data rows
#             lob_final = override_lob if override_enabled and override_lob else "PVT CAR"
#             segment_final = override_segment if override_enabled and override_segment else "PVT CAR COMP + SAOD"
            
#             skip_words = {"total", "grand total", "average", "sum", ""}
            
#             for row_idx in range(data_start, df.shape[0]):
#                 geo_new = cell_to_str(df.iloc[row_idx, 0])
#                 geo_old = cell_to_str(df.iloc[row_idx, 1])
                
#                 if not geo_new or geo_new.lower() in skip_words:
#                     continue
                
#                 # Combine Geo New and Geo Old with hyphen
#                 combined_location = f"{geo_new} - {geo_old}" if geo_old else geo_new
                
#                 # Extract state from geo_old (more specific)
#                 state = map_state(geo_old if geo_old else geo_new)
                
#                 # Process each column
#                 for m in col_meta:
#                     payin = safe_float(df.iloc[row_idx, m["col_idx"]])
                    
#                     if payin is None or payin == 0:
#                         continue
                    
#                     payout, formula, explanation = calculate_payout(payin, lob_final, segment_final)
                    
#                     records.append({
#                         "State": state,
#                         "Geo Location": combined_location,
#                         "Geo New": geo_new,
#                         "Geo Old": geo_old,
#                         "Original Segment": m["header"],
#                         "Mapped Segment": segment_final,
#                         "LOB": lob_final,
#                         "Policy Type": m["policy_type"],
#                         "Status": "STP",
#                         "Payin (OD Premium)": f"{payin:.2f}%",
#                         "Calculated Payout": f"{payout:.2f}%",
#                         "Formula Used": formula,
#                         "Rule Explanation": explanation,
#                     })
            
#             print(f"[GEO_NEW_OLD_COMP] Extracted {len(records)} records")
#             return records
            
#         except Exception as e:
#             print(f"[GEO_NEW_OLD_COMP] Error: {e}")
#             traceback.print_exc()
#             return []


# # ===============================================================================
# # GEO NEW/OLD SATP PROCESSOR
# # ===============================================================================

# class GeoNewOldSATPProcessor:
#     """Process SATP sheets with Geo segment New and Geo segment Old columns."""
    
#     @staticmethod
#     def process(content: bytes, sheet_name: str,
#                 override_enabled: bool = False,
#                 override_lob: str = None,
#                 override_segment: str = None) -> List[Dict]:
#         """
#         Process pattern:
#         Row 1: Title (March 2025 PAYOUT - PCSATP)
#         Row 2: Geo segment New | Geo segment Old | SATP Petrol | SATP Diesel
#         Row 3: (empty) | (empty) | <1000 cc | 1000-1500 cc | >1500 cc | ...
#         Row 4+: Data rows
#         """
#         records = []
        
#         try:
#             df = pd.read_excel(io.BytesIO(content), sheet_name=sheet_name, header=None)
            
#             print(f"\n[GEO_NEW_OLD_SATP] Processing sheet: {sheet_name}")
#             print(f"[GEO_NEW_OLD_SATP] Sheet shape: {df.shape}")
            
#             # Find header row with "Geo segment New"
#             header_row = None
#             for i in range(min(10, df.shape[0])):
#                 row_text = " ".join(cell_to_str(v) for v in df.iloc[i]).upper()
#                 if "GEO SEGMENT NEW" in row_text:
#                     header_row = i
#                     break
            
#             if header_row is None:
#                 print("[GEO_NEW_OLD_SATP] Header row not found")
#                 return records
            
#             print(f"[GEO_NEW_OLD_SATP] Found header row at index: {header_row}")
            
#             # CC band row is next
#             cc_row = header_row + 1
#             data_start = cc_row + 1
            
#             # Build column metadata (starting from column 2)
#             col_meta = []
#             last_fuel = ""
            
#             for col_idx in range(2, df.shape[1]):
#                 fuel_type = cell_to_str(df.iloc[header_row, col_idx]).upper()
#                 cc_band = cell_to_str(df.iloc[cc_row, col_idx])
                
#                 if not fuel_type and not cc_band:
#                     continue
                
#                 # Determine fuel type
#                 if "PETROL" in fuel_type:
#                     last_fuel = "Petrol"
#                 elif "DIESEL" in fuel_type:
#                     last_fuel = "Diesel"
                
#                 fuel = last_fuel if last_fuel else "Unknown"
                
#                 # Build segment description
#                 segment_desc = f"SATP {fuel}"
#                 if cc_band:
#                     segment_desc += f" ({cc_band})"
                
#                 col_meta.append({
#                     "col_idx": col_idx,
#                     "fuel_type": fuel,
#                     "cc_band": cc_band,
#                     "segment_desc": segment_desc,
#                 })
            
#             if not col_meta:
#                 print("[GEO_NEW_OLD_SATP] No data columns found")
#                 return records
            
#             print(f"[GEO_NEW_OLD_SATP] Found {len(col_meta)} columns")
            
#             # Process data rows
#             lob_final = override_lob if override_enabled and override_lob else "PVT CAR"
#             segment_final = override_segment if override_enabled and override_segment else "PVT CAR TP"
            
#             skip_words = {"total", "grand total", "average", "sum", ""}
            
#             for row_idx in range(data_start, df.shape[0]):
#                 geo_new = cell_to_str(df.iloc[row_idx, 0])
#                 geo_old = cell_to_str(df.iloc[row_idx, 1])
                
#                 if not geo_new or geo_new.lower() in skip_words:
#                     continue
                
#                 # Combine Geo New and Geo Old with hyphen
#                 combined_location = f"{geo_new} - {geo_old}" if geo_old else geo_new
                
#                 # Extract state from geo_old
#                 state = map_state(geo_old if geo_old else geo_new)
                
#                 # Process each column
#                 for m in col_meta:
#                     payin = safe_float(df.iloc[row_idx, m["col_idx"]])
                    
#                     if payin is None or payin == 0:
#                         continue
                    
#                     payout, formula, explanation = calculate_payout(payin, lob_final, segment_final)
                    
#                     records.append({
#                         "State": state,
#                         "Geo Location": combined_location,
#                         "Geo New": geo_new,
#                         "Geo Old": geo_old,
#                         "Original Segment": m["segment_desc"],
#                         "Mapped Segment": segment_final,
#                         "LOB": lob_final,
#                         "Policy Type": "TP",
#                         "Status": "STP",
#                         "Payin (OD Premium)": f"{payin:.2f}%",
#                         "Calculated Payout": f"{payout:.2f}%",
#                         "Formula Used": formula,
#                         "Rule Explanation": explanation,
#                         "Fuel Type": m["fuel_type"],
#                         "CC Band": m["cc_band"],
#                     })
            
#             print(f"[GEO_NEW_OLD_SATP] Extracted {len(records)} records")
#             return records
            
#         except Exception as e:
#             print(f"[GEO_NEW_OLD_SATP] Error: {e}")
#             traceback.print_exc()
#             return []


# # ===============================================================================
# # SATP CC BAND PROCESSOR
# # ===============================================================================

# class SATPCCProcessor:
#     """Process SATP (Third Party) sheets with CC (Cubic Capacity) bands."""
    
#     @staticmethod
#     def process(content: bytes, sheet_name: str,
#                 override_enabled: bool = False,
#                 override_lob: str = None,
#                 override_segment: str = None) -> List[Dict]:
#         """
#         Process SATP CC Band pattern:
#         Row 1: Title (JAN 2025 PAYOUT - PC TP)
#         Row 2: Geo Locations | SATP Petrol | SATP Diesel
#         Row 3: (empty) | <1000 cc | 1000-1500 cc | >1500 cc | 1000-1500 cc | >1500 cc
#         Row 4+: Data rows
#         """
#         records = []
        
#         try:
#             df = pd.read_excel(io.BytesIO(content), sheet_name=sheet_name, header=None)
            
#             print(f"\n[SATP_CC] Processing sheet: {sheet_name}")
#             print(f"[SATP_CC] Sheet shape: {df.shape}")
            
#             # Find the "Geo Locations" header row
#             header_row = None
#             for i in range(min(10, df.shape[0])):
#                 row_text = cell_to_str(df.iloc[i, 0]).upper()
#                 if "GEO LOCATION" in row_text or "GEO LOC" in row_text:
#                     header_row = i
#                     break
            
#             if header_row is None:
#                 print("[SATP_CC] 'Geo Locations' header row not found")
#                 return records
            
#             print(f"[SATP_CC] Found header row at index: {header_row}")
            
#             # Row structure:
#             # header_row: Geo Locations | SATP Petrol | SATP Diesel
#             # header_row + 1: (empty) | <1000 cc | 1000-1500 cc | >1500 cc | ...
#             cc_row = header_row + 1
            
#             # Data starts after CC row
#             data_start = cc_row + 1
            
#             # Skip empty rows
#             for i in range(data_start, df.shape[0]):
#                 if cell_to_str(df.iloc[i, 0]):
#                     data_start = i
#                     break
            
#             print(f"[SATP_CC] CC row: {cc_row}, Data starts: {data_start}")
            
#             # Build column metadata
#             col_meta = []
#             for col_idx in range(1, df.shape[1]):
#                 fuel_type = cell_to_str(df.iloc[header_row, col_idx]).upper()
#                 cc_band = cell_to_str(df.iloc[cc_row, col_idx])
                
#                 if not fuel_type and not cc_band:
#                     continue
                
#                 # Determine fuel type from header
#                 if "PETROL" in fuel_type:
#                     fuel = "Petrol"
#                 elif "DIESEL" in fuel_type:
#                     fuel = "Diesel"
#                 else:
#                     # Use previous fuel type (for merged cells)
#                     if col_meta:
#                         fuel = col_meta[-1]["fuel_type"]
#                     else:
#                         fuel = "Unknown"
                
#                 # Build segment description
#                 segment_desc = f"SATP {fuel}"
#                 if cc_band:
#                     segment_desc += f" ({cc_band})"
                
#                 col_meta.append({
#                     "col_idx": col_idx,
#                     "fuel_type": fuel,
#                     "cc_band": cc_band,
#                     "segment_desc": segment_desc,
#                 })
            
#             if not col_meta:
#                 print("[SATP_CC] No data columns found")
#                 return records
            
#             print(f"[SATP_CC] Found {len(col_meta)} columns")
#             for m in col_meta:
#                 print(f"  - Col {m['col_idx']}: {m['segment_desc']}")
            
#             # Process data rows
#             lob_final = override_lob if override_enabled and override_lob else "PVT CAR"
#             segment_final = override_segment if override_enabled and override_segment else "PVT CAR TP"
            
#             skip_words = {"total", "grand total", "average", "sum", ""}
            
#             for row_idx in range(data_start, df.shape[0]):
#                 geo_location = cell_to_str(df.iloc[row_idx, 0])
                
#                 if not geo_location or geo_location.lower() in skip_words:
#                     continue
                
#                 state = map_state(geo_location)
                
#                 # Process each column
#                 for m in col_meta:
#                     payin = safe_float(df.iloc[row_idx, m["col_idx"]])
                    
#                     if payin is None or payin == 0:
#                         continue
                    
#                     payout, formula, explanation = calculate_payout(payin, lob_final, segment_final)
                    
#                     records.append({
#                         "State": state,
#                         "Geo Location": geo_location,
#                         "Original Segment": m["segment_desc"],
#                         "Mapped Segment": segment_final,
#                         "LOB": lob_final,
#                         "Policy Type": "TP",
#                         "Status": "STP",
#                         "Payin (OD Premium)": f"{payin:.2f}%",
#                         "Calculated Payout": f"{payout:.2f}%",
#                         "Formula Used": formula,
#                         "Rule Explanation": explanation,
#                         "Fuel Type": m["fuel_type"],
#                         "CC Band": m["cc_band"],
#                     })
            
#             print(f"[SATP_CC] Extracted {len(records)} records")
#             return records
            
#         except Exception as e:
#             print(f"[SATP_CC] Error: {e}")
#             traceback.print_exc()
#             return []


# # ===============================================================================
# # COMP/SAOD PROCESSOR (Original Pattern)
# # ===============================================================================

# class CompSaodProcessor:
#     """Process COMP/SAOD pattern sheets."""
    
#     @staticmethod
#     def process(content: bytes, sheet_name: str,
#                 override_enabled: bool = False,
#                 override_lob: str = None,
#                 override_segment: str = None) -> List[Dict]:
#         """
#         Process Excel sheet with structure:
#         Row 0: Title row (JAN 2025 PAYOUT - PC COMP)
#         Row 1: Main headers (Geo Locations | Payout on | Segment columns)
#         Row 2-3: Empty or sub-headers
#         Row 4+: Data rows
#         """
#         records = []
        
#         try:
#             # Read Excel without header to inspect structure
#             df = pd.read_excel(io.BytesIO(content), sheet_name=sheet_name, header=None)
            
#             print(f"\n[COMP_SAOD] Processing sheet: {sheet_name}")
#             print(f"[COMP_SAOD] Sheet shape: {df.shape}")
            
#             # Find the header row (contains "Geo Locations")
#             header_row = None
#             for i in range(min(10, df.shape[0])):
#                 row_text = " ".join(cell_to_str(v) for v in df.iloc[i]).upper()
#                 if "GEO LOCATION" in row_text or "GEO LOC" in row_text:
#                     header_row = i
#                     break
            
#             if header_row is None:
#                 print("[COMP_SAOD] Could not find 'Geo Locations' header row")
#                 return records
            
#             print(f"[COMP_SAOD] Found header row at index: {header_row}")
            
#             # The actual data starts after header row
#             data_start = header_row + 1
            
#             # Skip any empty rows after header
#             for i in range(data_start, df.shape[0]):
#                 if cell_to_str(df.iloc[i, 0]):  # First column has content
#                     data_start = i
#                     break
            
#             print(f"[COMP_SAOD] Data starts at row: {data_start}")
            
#             # Build column metadata from header row
#             col_meta = []
#             for col_idx in range(2, df.shape[1]):  # Skip column 0 (Geo) and 1 (Payout on)
#                 header = cell_to_str(df.iloc[header_row, col_idx])
                
#                 if not header:
#                     continue
                
#                 # Determine policy type and segment from header
#                 header_upper = header.upper()
                
#                 if "COMP" in header_upper and "SOD" not in header_upper:
#                     policy_type = "COMP"
#                     segment = "PVT CAR COMP + SAOD"
#                 elif "SOD" in header_upper or "SAOD" in header_upper:
#                     policy_type = "SAOD"
#                     segment = "PVT CAR COMP + SAOD"
#                 elif "TP" in header_upper:
#                     policy_type = "TP"
#                     segment = "PVT CAR TP"
#                 else:
#                     policy_type = "COMP"
#                     segment = "PVT CAR COMP + SAOD"
                
#                 col_meta.append({
#                     "col_idx": col_idx,
#                     "header": header,
#                     "policy_type": policy_type,
#                     "segment": segment,
#                 })
            
#             if not col_meta:
#                 print("[COMP_SAOD] No data columns found")
#                 return records
            
#             print(f"[COMP_SAOD] Found {len(col_meta)} data columns")
#             for m in col_meta:
#                 print(f"  - Col {m['col_idx']}: {m['header']} -> {m['policy_type']}")
            
#             # Process data rows
#             lob_final = override_lob if override_enabled and override_lob else "PVT CAR"
            
#             skip_words = {"total", "grand total", "average", "sum", ""}
            
#             for row_idx in range(data_start, df.shape[0]):
#                 geo_location = cell_to_str(df.iloc[row_idx, 0])
                
#                 if not geo_location or geo_location.lower() in skip_words:
#                     continue
                
#                 state = map_state(geo_location)
                
#                 # Process each column
#                 for m in col_meta:
#                     payin = safe_float(df.iloc[row_idx, m["col_idx"]])
                    
#                     if payin is None or payin == 0:
#                         continue
                    
#                     segment_final = override_segment if override_enabled and override_segment else m["segment"]
                    
#                     payout, formula, explanation = calculate_payout(payin, lob_final, segment_final)
                    
#                     records.append({
#                         "State": state,
#                         "Geo Location": geo_location,
#                         "Original Segment": m["header"],
#                         "Mapped Segment": segment_final,
#                         "LOB": lob_final,
#                         "Policy Type": m["policy_type"],
#                         "Status": "STP",
#                         "Payin (OD Premium)": f"{payin:.2f}%",
#                         "Calculated Payout": f"{payout:.2f}%",
#                         "Formula Used": formula,
#                         "Rule Explanation": explanation,
#                     })
            
#             print(f"[COMP_SAOD] Extracted {len(records)} records")
#             return records
            
#         except Exception as e:
#             print(f"[COMP_SAOD] Error: {e}")
#             traceback.print_exc()
#             return []


# # ===============================================================================
# # PATTERN DISPATCHER
# # ===============================================================================

# class PatternDispatcher:
#     """Route to the correct processor based on detected pattern."""
    
#     PATTERN_PROCESSORS = {
#         "comp_saod": CompSaodProcessor,
#         "satp_cc": SATPCCProcessor,
#         "geo_new_old_comp": GeoNewOldCompProcessor,
#         "geo_new_old_satp": GeoNewOldSATPProcessor,
#     }
    
#     @staticmethod
#     def process_sheet(content: bytes, sheet_name: str,
#                       override_enabled: bool = False,
#                       override_lob: str = None,
#                       override_segment: str = None) -> List[Dict]:
#         """Detect pattern and route to appropriate processor."""
#         # Read raw data to detect pattern
#         df_raw = pd.read_excel(io.BytesIO(content), sheet_name=sheet_name, header=None)
#         pattern = PatternDetector.detect_pattern(df_raw)
        
#         print(f"\n[DISPATCHER] Detected pattern: {pattern}")
        
#         processor_class = PatternDispatcher.PATTERN_PROCESSORS.get(pattern, CompSaodProcessor)
#         return processor_class.process(
#             content, sheet_name,
#             override_enabled, override_lob, override_segment
#         )
#         """
#         Process Excel sheet with structure:
#         Row 0: Title row (JAN 2025 PAYOUT - PC COMP)
#         Row 1: Main headers (Geo Locations | Payout on | Segment columns)
#         Row 2-3: Empty or sub-headers
#         Row 4+: Data rows
#         """
#         records = []
        
#         try:
#             # Read Excel without header to inspect structure
#             df = pd.read_excel(io.BytesIO(content), sheet_name=sheet_name, header=None)
            
#             print(f"\n[PROCESSOR] Processing sheet: {sheet_name}")
#             print(f"[PROCESSOR] Sheet shape: {df.shape}")
            
#             # Find the header row (contains "Geo Locations")
#             header_row = None
#             for i in range(min(10, df.shape[0])):
#                 row_text = " ".join(cell_to_str(v) for v in df.iloc[i]).upper()
#                 if "GEO LOCATION" in row_text or "GEO LOC" in row_text:
#                     header_row = i
#                     break
            
#             if header_row is None:
#                 print("[PROCESSOR] Could not find 'Geo Locations' header row")
#                 return records
            
#             print(f"[PROCESSOR] Found header row at index: {header_row}")
            
#             # The actual data starts after header row
#             data_start = header_row + 1
            
#             # Skip any empty rows after header
#             for i in range(data_start, df.shape[0]):
#                 if cell_to_str(df.iloc[i, 0]):  # First column has content
#                     data_start = i
#                     break
            
#             print(f"[PROCESSOR] Data starts at row: {data_start}")
            
#             # Build column metadata from header row
#             col_meta = []
#             for col_idx in range(2, df.shape[1]):  # Skip column 0 (Geo) and 1 (Payout on)
#                 header = cell_to_str(df.iloc[header_row, col_idx])
                
#                 if not header:
#                     continue
                
#                 # Determine policy type and segment from header
#                 header_upper = header.upper()
                
#                 if "COMP" in header_upper and "SOD" not in header_upper:
#                     policy_type = "COMP"
#                     segment = "PVT CAR COMP + SAOD"
#                 elif "SOD" in header_upper or "SAOD" in header_upper:
#                     policy_type = "SAOD"
#                     segment = "PVT CAR COMP + SAOD"
#                 elif "TP" in header_upper:
#                     policy_type = "TP"
#                     segment = "PVT CAR TP"
#                 else:
#                     policy_type = "COMP"
#                     segment = "PVT CAR COMP + SAOD"
                
#                 col_meta.append({
#                     "col_idx": col_idx,
#                     "header": header,
#                     "policy_type": policy_type,
#                     "segment": segment,
#                 })
            
#             if not col_meta:
#                 print("[PROCESSOR] No data columns found")
#                 return records
            
#             print(f"[PROCESSOR] Found {len(col_meta)} data columns")
#             for m in col_meta:
#                 print(f"  - Col {m['col_idx']}: {m['header']} -> {m['policy_type']}")
            
#             # Process data rows
#             lob_final = override_lob if override_enabled and override_lob else "PVT CAR"
            
#             skip_words = {"total", "grand total", "average", "sum", ""}
            
#             for row_idx in range(data_start, df.shape[0]):
#                 geo_location = cell_to_str(df.iloc[row_idx, 0])
                
#                 if not geo_location or geo_location.lower() in skip_words:
#                     continue
                
#                 state = map_state(geo_location)
                
#                 # Process each column
#                 for m in col_meta:
#                     payin = safe_float(df.iloc[row_idx, m["col_idx"]])
                    
#                     if payin is None or payin == 0:
#                         continue
                    
#                     segment_final = override_segment if override_enabled and override_segment else m["segment"]
                    
#                     payout, formula, explanation = calculate_payout(payin, lob_final, segment_final)
                    
#                     records.append({
#                         "State": state,
#                         "Geo Location": geo_location,
#                         "Original Segment": m["header"],
#                         "Mapped Segment": segment_final,
#                         "LOB": lob_final,
#                         "Policy Type": m["policy_type"],
#                         "Status": "STP",
#                         "Payin (OD Premium)": f"{payin:.2f}%",
#                         "Calculated Payout": f"{payout:.2f}%",
#                         "Formula Used": formula,
#                         "Rule Explanation": explanation,
#                     })
            
#             print(f"[PROCESSOR] Extracted {len(records)} records")
#             return records
            
#         except Exception as e:
#             print(f"[PROCESSOR] Error: {e}")
#             traceback.print_exc()
#             return []


# # ===============================================================================
# # API ENDPOINTS
# # ===============================================================================

# @app.get("/")
# async def root():
#     return {
#         "message": "Insurance Payout Processor API",
#         "version": "3.0.0",
#         "formula": "90% of Payin for all segments",
#         "supported_lobs": ["PVT CAR"],
#         "supported_segments": ["PVT CAR COMP + SAOD", "PVT CAR TP"],
#         "supported_patterns": [
#             "comp_saod - COMP/SAOD with fuel types (Petrol, Diesel, NCB variants)",
#             "satp_cc - SATP (Third Party) with CC bands (<1000cc, 1000-1500cc, >1500cc)",
#             "geo_new_old_comp - COMP with Geo segment New/Old columns",
#             "geo_new_old_satp - SATP with Geo segment New/Old columns"
#         ]
#     }


# @app.post("/upload")
# async def upload_file(file: UploadFile = File(...)):
#     """Upload Excel file and return worksheet list."""
#     try:
#         if not file.filename.endswith((".xlsx", ".xls")):
#             raise HTTPException(status_code=400, detail="Only Excel files are supported")
        
#         content = await file.read()
#         xls = pd.ExcelFile(io.BytesIO(content))
#         sheets = xls.sheet_names
        
#         file_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
#         uploaded_files[file_id] = {
#             "content": content,
#             "filename": file.filename,
#             "sheets": sheets,
#         }
        
#         return {
#             "file_id": file_id,
#             "filename": file.filename,
#             "sheets": sheets,
#             "message": f"Uploaded successfully. {len(sheets)} worksheet(s) found.",
#         }
        
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Upload error: {str(e)}")


# @app.post("/process")
# async def process_sheet(
#     file_id: str,
#     sheet_name: str,
#     override_enabled: bool = False,
#     override_lob: Optional[str] = None,
#     override_segment: Optional[str] = None,
# ):
#     """Process a specific worksheet."""
#     try:
#         if file_id not in uploaded_files:
#             raise HTTPException(status_code=404, detail="File not found. Please re-upload.")
        
#         file_data = uploaded_files[file_id]
        
#         if sheet_name not in file_data["sheets"]:
#             raise HTTPException(status_code=400, detail=f"Sheet '{sheet_name}' not found")
        
#         # Use PatternDispatcher to automatically detect and process
#         records = PatternDispatcher.process_sheet(
#             file_data["content"], 
#             sheet_name,
#             override_enabled, 
#             override_lob, 
#             override_segment,
#         )
        
#         if not records:
#             return {
#                 "success": False,
#                 "message": "No records extracted. Check sheet structure.",
#                 "records": [],
#                 "count": 0,
#             }
        
#         # Calculate summary statistics
#         states = {}
#         policies = {}
#         payins = []
#         payouts = []
        
#         for r in records:
#             state = r.get("State", "UNKNOWN")
#             states[state] = states.get(state, 0) + 1
            
#             policy = r.get("Policy Type", "UNKNOWN")
#             policies[policy] = policies.get(policy, 0) + 1
            
#             try:
#                 payin_val = float(r.get("Payin (OD Premium)", "0%").replace("%", ""))
#                 payout_val = float(r.get("Calculated Payout", "0%").replace("%", ""))
#                 payins.append(payin_val)
#                 payouts.append(payout_val)
#             except Exception:
#                 pass
        
#         avg_payin = round(sum(payins) / len(payins), 2) if payins else 0
#         avg_payout = round(sum(payouts) / len(payouts), 2) if payouts else 0
        
#         return {
#             "success": True,
#             "message": f"Successfully processed {len(records)} records from '{sheet_name}'",
#             "records": records,
#             "count": len(records),
#             "summary": {
#                 "total_records": len(records),
#                 "states": dict(sorted(states.items(), key=lambda x: x[1], reverse=True)[:10]),
#                 "policy_types": policies,
#                 "average_payin": avg_payin,
#                 "average_payout": avg_payout,
#             },
#         }
        
#     except Exception as e:
#         traceback.print_exc()
#         raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")


# @app.post("/export")
# async def export_to_excel(file_id: str, sheet_name: str, records: List[Dict]):
#     """Export processed records to Excel."""
#     try:
#         if not records:
#             raise HTTPException(status_code=400, detail="No records to export")
        
#         df = pd.DataFrame(records)
        
#         timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#         filename = f"Processed_{sheet_name.replace(' ', '_')}_{timestamp}.xlsx"
#         out_path = os.path.join(tempfile.gettempdir(), filename)
        
#         # Create Excel writer with formatting
#         with pd.ExcelWriter(out_path, engine='openpyxl') as writer:
#             df.to_excel(writer, index=False, sheet_name="Processed Data")
            
#             # Auto-adjust column widths
#             worksheet = writer.sheets["Processed Data"]
#             for idx, col in enumerate(df.columns):
#                 max_length = max(
#                     df[col].astype(str).apply(len).max(),
#                     len(str(col))
#                 )
#                 worksheet.column_dimensions[chr(65 + idx)].width = min(max_length + 2, 50)
        
#         return FileResponse(
#             path=out_path,
#             filename=filename,
#             media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
#         )
        
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Export error: {str(e)}")


# @app.get("/health")
# async def health_check():
#     """Health check endpoint."""
#     return {
#         "status": "healthy",
#         "timestamp": datetime.now().isoformat(),
#         "uploaded_files": len(uploaded_files)
#     }


# if __name__ == "__main__":
#     import uvicorn
#     print("\n" + "=" * 70)
#     print("Insurance Payout Processor API - v3.0.0")
#     print("Formula: 90% of Payin for all PVT CAR segments")
#     print("Patterns: COMP/SAOD + SATP (with CC bands) + Geo New/Old")
#     print("=" * 70 + "\n")
#     uvicorn.run(app, host="0.0.0.0", port=8000)





# from fastapi import FastAPI, File, UploadFile, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import FileResponse, JSONResponse
# import pandas as pd
# import io
# import os
# from typing import List, Dict, Tuple, Optional
# from datetime import datetime
# import traceback
# import tempfile

# app = FastAPI(title="Insurance Payout Processor API")

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Update with your frontend URL
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # ===============================================================================
# # FORMULA DATA
# # ===============================================================================
# FORMULA_DATA = [
#     {"LOB": "PVT CAR", "SEGMENT": "PVT CAR COMP + SAOD", "PO": "90% of Payin", "REMARKS": "NIL"},
#     {"LOB": "PVT CAR", "SEGMENT": "PVT CAR TP", "PO": "90% of Payin", "REMARKS": "NIL"},
# ]

# # ===============================================================================
# # STATE MAPPING
# # ===============================================================================
# STATE_MAPPING = {
#     "ANDHRA PRADESH": "ANDHRA PRADESH",
#     "KRISHNA": "ANDHRA PRADESH",
#     "VIJAYWADA": "ANDHRA PRADESH",
#     "VIJAYAWADA": "ANDHRA PRADESH",
#     "VISAKHAPATNAM": "ANDHRA PRADESH",
#     "VIZAG": "ANDHRA PRADESH",
    
#     "KARNATAKA": "KARNATAKA",
#     "BANGALORE": "KARNATAKA",
#     "BENGALURU": "KARNATAKA",
#     "MYSORE": "KARNATAKA",
#     "MANGALORE": "KARNATAKA",
    
#     "KERALA": "KERALA",
#     "ERNAKULAM": "KERALA",
#     "COCHIN": "KERALA",
#     "KOCHI": "KERALA",
#     "TRIVANDRUM": "KERALA",
#     "CALICUT": "KERALA",
#     "KOZHIKODE": "KERALA",
    
#     "TAMIL NADU": "TAMIL NADU",
#     "CHENNAI": "TAMIL NADU",
#     "MADRAS": "TAMIL NADU",
#     "PONDICHERRY": "TAMIL NADU",
#     "PUDUCHERRY": "TAMIL NADU",
#     "COIMBATORE": "TAMIL NADU",
#     "MADURAI": "TAMIL NADU",
    
#     "TELANGANA": "TELANGANA",
#     "HYDERABAD": "TELANGANA",
#     "SECUNDERABAD": "TELANGANA",
    
#     "MAHARASHTRA": "MAHARASHTRA",
#     "MUMBAI": "MAHARASHTRA",
#     "PUNE": "MAHARASHTRA",
#     "NAGPUR": "MAHARASHTRA",
#     "THANE": "MAHARASHTRA",
#     "NASHIK": "MAHARASHTRA",
    
#     "DELHI": "DELHI",
#     "NEW DELHI": "DELHI",
#     "NCR": "DELHI",
    
#     "GUJARAT": "GUJARAT",
#     "AHMEDABAD": "GUJARAT",
#     "SURAT": "GUJARAT",
#     "VADODARA": "GUJARAT",
#     "RAJKOT": "GUJARAT",
    
#     "RAJASTHAN": "RAJASTHAN",
#     "JAIPUR": "RAJASTHAN",
#     "JODHPUR": "RAJASTHAN",
#     "UDAIPUR": "RAJASTHAN",
    
#     "UTTAR PRADESH": "UTTAR PRADESH",
#     "LUCKNOW": "UTTAR PRADESH",
#     "KANPUR": "UTTAR PRADESH",
#     "AGRA": "UTTAR PRADESH",
#     "VARANASI": "UTTAR PRADESH",
#     "NOIDA": "UTTAR PRADESH",
    
#     "WEST BENGAL": "WEST BENGAL",
#     "KOLKATA": "WEST BENGAL",
#     "CALCUTTA": "WEST BENGAL",
    
#     "MADHYA PRADESH": "MADHYA PRADESH",
#     "BHOPAL": "MADHYA PRADESH",
#     "INDORE": "MADHYA PRADESH",
    
#     "PUNJAB": "PUNJAB",
#     "CHANDIGARH": "CHANDIGARH",
#     "HARYANA": "HARYANA",
#     "GOA": "GOA",
#     "BIHAR": "BIHAR",
#     "PATNA": "BIHAR",
#     "JHARKHAND": "JHARKHAND",
#     "RANCHI": "JHARKHAND",
#     "ODISHA": "ODISHA",
#     "BHUBANESWAR": "ODISHA",
#     "ASSAM": "ASSAM",
#     "GUWAHATI": "ASSAM",
# }

# uploaded_files = {}

# # ===============================================================================
# # HELPER FUNCTIONS
# # ===============================================================================

# def cell_to_str(val) -> str:
#     """Safely convert ANY cell value (float NaN, None, int, str) to string."""
#     if val is None:
#         return ""
#     try:
#         if pd.isna(val):
#             return ""
#     except (TypeError, ValueError):
#         pass
#     return str(val).strip()


# def safe_float(value) -> Optional[float]:
#     """Safely convert value to float, handling percentages and invalid values."""
#     if value is None:
#         return None
#     try:
#         if pd.isna(value):
#             return None
#     except (TypeError, ValueError):
#         pass
    
#     s = str(value).strip().upper().replace("%", "")
#     if s in ["D", "NA", "", "NAN", "NONE", "DECLINE", "0.00%", "0.0%", "0%"]:
#         return None
    
#     try:
#         num = float(s)
#         if num < 0:
#             return None
#         # Convert decimals to percentages (0.28 -> 28%)
#         return num * 100 if 0 < num < 1 else num
#     except Exception:
#         return None


# def map_state(location: str) -> str:
#     """Map location/geo name to state using STATE_MAPPING."""
#     location_upper = location.upper()
    
#     # Direct match first
#     for key, val in STATE_MAPPING.items():
#         if key.upper() == location_upper:
#             return val
    
#     # Partial match
#     for key, val in STATE_MAPPING.items():
#         if key.upper() in location_upper:
#             return val
    
#     return location  # Return original if no match


# def calculate_payout(payin: float, lob: str = "PVT CAR", segment: str = "PVT CAR COMP + SAOD") -> Tuple[float, str, str]:
#     """
#     Calculate payout based on formula: 90% of Payin
#     """
#     if payin == 0 or payin is None:
#         return 0, "0% (No Payin)", "Payin is 0"
    
#     # Formula: 90% of Payin
#     payout = round(payin * 0.90, 2)
#     formula = "90% of Payin"
#     explanation = f"Applied formula: {formula} for {segment}"
    
#     return payout, formula, explanation


# # ===============================================================================
# # PATTERN DETECTION
# # ===============================================================================

# class PatternDetector:
#     """Detect the pattern type of the Excel sheet."""
    
#     @staticmethod
#     def detect_pattern(df: pd.DataFrame) -> str:
#         """
#         Detect pattern type:
#         - 'comp_saod': COMP/SAOD pattern (Comp - Petrol, SOD - NCB, etc.)
#         - 'satp_cc': SATP with CC bands (<1000 cc, 1000-1500 cc, >1500 cc)
#         - 'geo_new_old_comp': COMP pattern with Geo segment New/Old columns
#         - 'geo_new_old_satp': SATP pattern with Geo segment New/Old columns
#         - 'zone_geo_comp': COMP pattern with Zone + Geo segment Old columns
#         - 'zone_geo_satp': SATP pattern with Zone + Geo segment Old columns
#         """
#         # Check first 10 rows for pattern indicators
#         sample_text = ""
#         for i in range(min(10, df.shape[0])):
#             row_text = " ".join(cell_to_str(v) for v in df.iloc[i]).upper()
#             sample_text += row_text + " "
        
#         # Check for Zone + Geo segment Old pattern
#         has_zone = "ZONE" in sample_text and "GEO SEGMENT OLD" in sample_text
        
#         if has_zone:
#             # Determine if it's COMP or SATP
#             if "COMP" in sample_text or "SOD" in sample_text:
#                 return "zone_geo_comp"
#             elif "SATP" in sample_text or "SA TP" in sample_text:
#                 return "zone_geo_satp"
        
#         # Check for Geo segment New/Old pattern
#         has_geo_new = "GEO SEGMENT NEW" in sample_text or "GEO SEGMENT OLD" in sample_text
        
#         if has_geo_new:
#             # Determine if it's COMP or SATP
#             if "PCCOMP" in sample_text or "PC COMP" in sample_text or "PAYOUT - PCCOMP" in sample_text:
#                 return "geo_new_old_comp"
#             elif "PCSATP" in sample_text or "PC SATP" in sample_text or "SATP" in sample_text:
#                 return "geo_new_old_satp"
        
#         # SATP CC Band pattern detection
#         if ("SATP" in sample_text or "SA TP" in sample_text) and ("CC" in sample_text or "1000" in sample_text):
#             return "satp_cc"
        
#         # COMP/SAOD pattern (default)
#         return "comp_saod"


# # ===============================================================================
# # ZONE + GEO OLD COMP PROCESSOR
# # ===============================================================================

# class ZoneGeoCompProcessor:
#     """Process COMP sheets with Zone and Geo segment Old columns."""
    
#     @staticmethod
#     def process(content: bytes, sheet_name: str,
#                 override_enabled: bool = False,
#                 override_lob: str = None,
#                 override_segment: str = None) -> List[Dict]:
#         """
#         Process pattern:
#         Row 3: Zone | Geo segment Old | Comp - Petrol - NCB / NON NCB | ...
#         Row 4+: Data rows (Zone | Geo Old | payin values)
        
#         Combined location format: "Zone - Geo segment Old"
#         Example: "South - ANDHRA PRADESH - KRISHNA(VIJAYWADA)"
#         """
#         records = []
        
#         try:
#             df = pd.read_excel(io.BytesIO(content), sheet_name=sheet_name, header=None)
            
#             print(f"\n[ZONE_GEO_COMP] Processing sheet: {sheet_name}")
#             print(f"[ZONE_GEO_COMP] Sheet shape: {df.shape}")
            
#             # Find header row with "Zone" and "Geo segment Old"
#             header_row = None
#             for i in range(min(10, df.shape[0])):
#                 row_text = " ".join(cell_to_str(v) for v in df.iloc[i]).upper()
#                 if "ZONE" in row_text and "GEO SEGMENT OLD" in row_text:
#                     header_row = i
#                     break
            
#             if header_row is None:
#                 print("[ZONE_GEO_COMP] Header row not found")
#                 return records
            
#             print(f"[ZONE_GEO_COMP] Found header row at index: {header_row}")
            
#             # Data starts after header
#             data_start = header_row + 1
            
#             # Skip empty rows
#             for i in range(data_start, df.shape[0]):
#                 if cell_to_str(df.iloc[i, 0]) or cell_to_str(df.iloc[i, 1]):
#                     data_start = i
#                     break
            
#             # Build column metadata (starting from column 2, after Zone and Geo Old)
#             col_meta = []
#             for col_idx in range(2, df.shape[1]):
#                 header = cell_to_str(df.iloc[header_row, col_idx])
                
#                 if not header:
#                     continue
                
#                 header_upper = header.upper()
                
#                 # Determine policy type
#                 if "COMP" in header_upper and "SOD" not in header_upper and "SAOD" not in header_upper:
#                     policy_type = "COMP"
#                 elif "SOD" in header_upper or "SAOD" in header_upper:
#                     policy_type = "SAOD"
#                 else:
#                     policy_type = "COMP"
                
#                 col_meta.append({
#                     "col_idx": col_idx,
#                     "header": header,
#                     "policy_type": policy_type,
#                 })
            
#             if not col_meta:
#                 print("[ZONE_GEO_COMP] No data columns found")
#                 return records
            
#             print(f"[ZONE_GEO_COMP] Found {len(col_meta)} columns")
            
#             # Process data rows
#             lob_final = override_lob if override_enabled and override_lob else "PVT CAR"
#             segment_final = override_segment if override_enabled and override_segment else "PVT CAR COMP + SAOD"
            
#             skip_words = {"total", "grand total", "average", "sum", ""}
            
#             for row_idx in range(data_start, df.shape[0]):
#                 zone = cell_to_str(df.iloc[row_idx, 0])
#                 geo_old = cell_to_str(df.iloc[row_idx, 1])
                
#                 if not geo_old or geo_old.lower() in skip_words:
#                     continue
                
#                 # Combine Zone and Geo Old with hyphen
#                 combined_location = f"{zone} - {geo_old}" if zone else geo_old
                
#                 # Extract state from geo_old
#                 state = map_state(geo_old)
                
#                 # Process each column
#                 for m in col_meta:
#                     payin = safe_float(df.iloc[row_idx, m["col_idx"]])
                    
#                     if payin is None or payin == 0:
#                         continue
                    
#                     payout, formula, explanation = calculate_payout(payin, lob_final, segment_final)
                    
#                     records.append({
#                         "State": state,
#                         "Geo Location": combined_location,
#                         "Zone": zone,
#                         "Geo Old": geo_old,
#                         "Original Segment": m["header"],
#                         "Mapped Segment": segment_final,
#                         "LOB": lob_final,
#                         "Policy Type": m["policy_type"],
#                         "Status": "STP",
#                         "Payin (OD Premium)": f"{payin:.2f}%",
#                         "Calculated Payout": f"{payout:.2f}%",
#                         "Formula Used": formula,
#                         "Rule Explanation": explanation,
#                     })
            
#             print(f"[ZONE_GEO_COMP] Extracted {len(records)} records")
#             return records
            
#         except Exception as e:
#             print(f"[ZONE_GEO_COMP] Error: {e}")
#             traceback.print_exc()
#             return []


# # ===============================================================================
# # ZONE + GEO OLD SATP PROCESSOR
# # ===============================================================================

# class ZoneGeoSATPProcessor:
#     """Process SATP sheets with Zone and Geo segment Old columns."""
    
#     @staticmethod
#     def process(content: bytes, sheet_name: str,
#                 override_enabled: bool = False,
#                 override_lob: str = None,
#                 override_segment: str = None) -> List[Dict]:
#         """
#         Process pattern:
#         Row X: Zone | Geo segment Old | SATP Petrol | SATP Diesel
#         Row X+1: (empty) | (empty) | <1000 cc | 1000-1500 cc | >1500 cc | ...
#         Row X+2+: Data rows
#         """
#         records = []
        
#         try:
#             df = pd.read_excel(io.BytesIO(content), sheet_name=sheet_name, header=None)
            
#             print(f"\n[ZONE_GEO_SATP] Processing sheet: {sheet_name}")
#             print(f"[ZONE_GEO_SATP] Sheet shape: {df.shape}")
            
#             # Find header row with "Zone"
#             header_row = None
#             for i in range(min(10, df.shape[0])):
#                 row_text = " ".join(cell_to_str(v) for v in df.iloc[i]).upper()
#                 if "ZONE" in row_text and ("GEO SEGMENT OLD" in row_text or "SATP" in row_text):
#                     header_row = i
#                     break
            
#             if header_row is None:
#                 print("[ZONE_GEO_SATP] Header row not found")
#                 return records
            
#             print(f"[ZONE_GEO_SATP] Found header row at index: {header_row}")
            
#             # CC band row is next
#             cc_row = header_row + 1
#             data_start = cc_row + 1
            
#             # Build column metadata (starting from column 2)
#             col_meta = []
#             last_fuel = ""
            
#             for col_idx in range(2, df.shape[1]):
#                 fuel_type = cell_to_str(df.iloc[header_row, col_idx]).upper()
#                 cc_band = cell_to_str(df.iloc[cc_row, col_idx])
                
#                 if not fuel_type and not cc_band:
#                     continue
                
#                 # Determine fuel type
#                 if "PETROL" in fuel_type:
#                     last_fuel = "Petrol"
#                 elif "DIESEL" in fuel_type:
#                     last_fuel = "Diesel"
                
#                 fuel = last_fuel if last_fuel else "Unknown"
                
#                 # Build segment description
#                 segment_desc = f"SATP {fuel}"
#                 if cc_band:
#                     segment_desc += f" ({cc_band})"
                
#                 col_meta.append({
#                     "col_idx": col_idx,
#                     "fuel_type": fuel,
#                     "cc_band": cc_band,
#                     "segment_desc": segment_desc,
#                 })
            
#             if not col_meta:
#                 print("[ZONE_GEO_SATP] No data columns found")
#                 return records
            
#             print(f"[ZONE_GEO_SATP] Found {len(col_meta)} columns")
            
#             # Process data rows
#             lob_final = override_lob if override_enabled and override_lob else "PVT CAR"
#             segment_final = override_segment if override_enabled and override_segment else "PVT CAR TP"
            
#             skip_words = {"total", "grand total", "average", "sum", ""}
            
#             for row_idx in range(data_start, df.shape[0]):
#                 zone = cell_to_str(df.iloc[row_idx, 0])
#                 geo_old = cell_to_str(df.iloc[row_idx, 1])
                
#                 if not geo_old or geo_old.lower() in skip_words:
#                     continue
                
#                 # Combine Zone and Geo Old with hyphen
#                 combined_location = f"{zone} - {geo_old}" if zone else geo_old
                
#                 # Extract state from geo_old
#                 state = map_state(geo_old)
                
#                 # Process each column
#                 for m in col_meta:
#                     payin = safe_float(df.iloc[row_idx, m["col_idx"]])
                    
#                     if payin is None or payin == 0:
#                         continue
                    
#                     payout, formula, explanation = calculate_payout(payin, lob_final, segment_final)
                    
#                     records.append({
#                         "State": state,
#                         "Geo Location": combined_location,
#                         "Zone": zone,
#                         "Geo Old": geo_old,
#                         "Original Segment": m["segment_desc"],
#                         "Mapped Segment": segment_final,
#                         "LOB": lob_final,
#                         "Policy Type": "TP",
#                         "Status": "STP",
#                         "Payin (OD Premium)": f"{payin:.2f}%",
#                         "Calculated Payout": f"{payout:.2f}%",
#                         "Formula Used": formula,
#                         "Rule Explanation": explanation,
#                         "Fuel Type": m["fuel_type"],
#                         "CC Band": m["cc_band"],
#                     })
            
#             print(f"[ZONE_GEO_SATP] Extracted {len(records)} records")
#             return records
            
#         except Exception as e:
#             print(f"[ZONE_GEO_SATP] Error: {e}")
#             traceback.print_exc()
#             return []


# # ===============================================================================
# # GEO NEW/OLD COMP PROCESSOR
# # ===============================================================================

# class GeoNewOldCompProcessor:
#     """Process COMP sheets with Geo segment New and Geo segment Old columns."""
    
#     @staticmethod
#     def process(content: bytes, sheet_name: str,
#                 override_enabled: bool = False,
#                 override_lob: str = None,
#                 override_segment: str = None) -> List[Dict]:
#         """
#         Process pattern:
#         Row 1: Title (March 2025 PAYOUT - PCCOMP)
#         Row 2: Empty
#         Row 3: Geo segment New | Geo segment Old | Comp - Petrol - NCB / NON NCB | ...
#         Row 4+: Data rows
#         """
#         records = []
        
#         try:
#             df = pd.read_excel(io.BytesIO(content), sheet_name=sheet_name, header=None)
            
#             print(f"\n[GEO_NEW_OLD_COMP] Processing sheet: {sheet_name}")
#             print(f"[GEO_NEW_OLD_COMP] Sheet shape: {df.shape}")
            
#             # Find header row with "Geo segment New"
#             header_row = None
#             for i in range(min(10, df.shape[0])):
#                 row_text = " ".join(cell_to_str(v) for v in df.iloc[i]).upper()
#                 if "GEO SEGMENT NEW" in row_text:
#                     header_row = i
#                     break
            
#             if header_row is None:
#                 print("[GEO_NEW_OLD_COMP] Header row not found")
#                 return records
            
#             print(f"[GEO_NEW_OLD_COMP] Found header row at index: {header_row}")
            
#             # Data starts after header
#             data_start = header_row + 1
            
#             # Build column metadata (starting from column 2, after Geo New and Geo Old)
#             col_meta = []
#             for col_idx in range(2, df.shape[1]):
#                 header = cell_to_str(df.iloc[header_row, col_idx])
                
#                 if not header:
#                     continue
                
#                 header_upper = header.upper()
                
#                 # Determine policy type
#                 if "COMP" in header_upper and "SOD" not in header_upper and "SAOD" not in header_upper:
#                     policy_type = "COMP"
#                 elif "SOD" in header_upper or "SAOD" in header_upper:
#                     policy_type = "SAOD"
#                 else:
#                     policy_type = "COMP"
                
#                 col_meta.append({
#                     "col_idx": col_idx,
#                     "header": header,
#                     "policy_type": policy_type,
#                 })
            
#             if not col_meta:
#                 print("[GEO_NEW_OLD_COMP] No data columns found")
#                 return records
            
#             print(f"[GEO_NEW_OLD_COMP] Found {len(col_meta)} columns")
            
#             # Process data rows
#             lob_final = override_lob if override_enabled and override_lob else "PVT CAR"
#             segment_final = override_segment if override_enabled and override_segment else "PVT CAR COMP + SAOD"
            
#             skip_words = {"total", "grand total", "average", "sum", ""}
            
#             for row_idx in range(data_start, df.shape[0]):
#                 geo_new = cell_to_str(df.iloc[row_idx, 0])
#                 geo_old = cell_to_str(df.iloc[row_idx, 1])
                
#                 if not geo_new or geo_new.lower() in skip_words:
#                     continue
                
#                 # Combine Geo New and Geo Old with hyphen
#                 combined_location = f"{geo_new} - {geo_old}" if geo_old else geo_new
                
#                 # Extract state from geo_old (more specific)
#                 state = map_state(geo_old if geo_old else geo_new)
                
#                 # Process each column
#                 for m in col_meta:
#                     payin = safe_float(df.iloc[row_idx, m["col_idx"]])
                    
#                     if payin is None or payin == 0:
#                         continue
                    
#                     payout, formula, explanation = calculate_payout(payin, lob_final, segment_final)
                    
#                     records.append({
#                         "State": state,
#                         "Geo Location": combined_location,
#                         "Geo New": geo_new,
#                         "Geo Old": geo_old,
#                         "Original Segment": m["header"],
#                         "Mapped Segment": segment_final,
#                         "LOB": lob_final,
#                         "Policy Type": m["policy_type"],
#                         "Status": "STP",
#                         "Payin (OD Premium)": f"{payin:.2f}%",
#                         "Calculated Payout": f"{payout:.2f}%",
#                         "Formula Used": formula,
#                         "Rule Explanation": explanation,
#                     })
            
#             print(f"[GEO_NEW_OLD_COMP] Extracted {len(records)} records")
#             return records
            
#         except Exception as e:
#             print(f"[GEO_NEW_OLD_COMP] Error: {e}")
#             traceback.print_exc()
#             return []


# # ===============================================================================
# # GEO NEW/OLD SATP PROCESSOR
# # ===============================================================================

# class GeoNewOldSATPProcessor:
#     """Process SATP sheets with Geo segment New and Geo segment Old columns."""
    
#     @staticmethod
#     def process(content: bytes, sheet_name: str,
#                 override_enabled: bool = False,
#                 override_lob: str = None,
#                 override_segment: str = None) -> List[Dict]:
#         """
#         Process pattern:
#         Row 1: Title (March 2025 PAYOUT - PCSATP)
#         Row 2: Geo segment New | Geo segment Old | SATP Petrol | SATP Diesel
#         Row 3: (empty) | (empty) | <1000 cc | 1000-1500 cc | >1500 cc | ...
#         Row 4+: Data rows
#         """
#         records = []
        
#         try:
#             df = pd.read_excel(io.BytesIO(content), sheet_name=sheet_name, header=None)
            
#             print(f"\n[GEO_NEW_OLD_SATP] Processing sheet: {sheet_name}")
#             print(f"[GEO_NEW_OLD_SATP] Sheet shape: {df.shape}")
            
#             # Find header row with "Geo segment New"
#             header_row = None
#             for i in range(min(10, df.shape[0])):
#                 row_text = " ".join(cell_to_str(v) for v in df.iloc[i]).upper()
#                 if "GEO SEGMENT NEW" in row_text:
#                     header_row = i
#                     break
            
#             if header_row is None:
#                 print("[GEO_NEW_OLD_SATP] Header row not found")
#                 return records
            
#             print(f"[GEO_NEW_OLD_SATP] Found header row at index: {header_row}")
            
#             # CC band row is next
#             cc_row = header_row + 1
#             data_start = cc_row + 1
            
#             # Build column metadata (starting from column 2)
#             col_meta = []
#             last_fuel = ""
            
#             for col_idx in range(2, df.shape[1]):
#                 fuel_type = cell_to_str(df.iloc[header_row, col_idx]).upper()
#                 cc_band = cell_to_str(df.iloc[cc_row, col_idx])
                
#                 if not fuel_type and not cc_band:
#                     continue
                
#                 # Determine fuel type
#                 if "PETROL" in fuel_type:
#                     last_fuel = "Petrol"
#                 elif "DIESEL" in fuel_type:
#                     last_fuel = "Diesel"
                
#                 fuel = last_fuel if last_fuel else "Unknown"
                
#                 # Build segment description
#                 segment_desc = f"SATP {fuel}"
#                 if cc_band:
#                     segment_desc += f" ({cc_band})"
                
#                 col_meta.append({
#                     "col_idx": col_idx,
#                     "fuel_type": fuel,
#                     "cc_band": cc_band,
#                     "segment_desc": segment_desc,
#                 })
            
#             if not col_meta:
#                 print("[GEO_NEW_OLD_SATP] No data columns found")
#                 return records
            
#             print(f"[GEO_NEW_OLD_SATP] Found {len(col_meta)} columns")
            
#             # Process data rows
#             lob_final = override_lob if override_enabled and override_lob else "PVT CAR"
#             segment_final = override_segment if override_enabled and override_segment else "PVT CAR TP"
            
#             skip_words = {"total", "grand total", "average", "sum", ""}
            
#             for row_idx in range(data_start, df.shape[0]):
#                 geo_new = cell_to_str(df.iloc[row_idx, 0])
#                 geo_old = cell_to_str(df.iloc[row_idx, 1])
                
#                 if not geo_new or geo_new.lower() in skip_words:
#                     continue
                
#                 # Combine Geo New and Geo Old with hyphen
#                 combined_location = f"{geo_new} - {geo_old}" if geo_old else geo_new
                
#                 # Extract state from geo_old
#                 state = map_state(geo_old if geo_old else geo_new)
                
#                 # Process each column
#                 for m in col_meta:
#                     payin = safe_float(df.iloc[row_idx, m["col_idx"]])
                    
#                     if payin is None or payin == 0:
#                         continue
                    
#                     payout, formula, explanation = calculate_payout(payin, lob_final, segment_final)
                    
#                     records.append({
#                         "State": state,
#                         "Geo Location": combined_location,
#                         "Geo New": geo_new,
#                         "Geo Old": geo_old,
#                         "Original Segment": m["segment_desc"],
#                         "Mapped Segment": segment_final,
#                         "LOB": lob_final,
#                         "Policy Type": "TP",
#                         "Status": "STP",
#                         "Payin (OD Premium)": f"{payin:.2f}%",
#                         "Calculated Payout": f"{payout:.2f}%",
#                         "Formula Used": formula,
#                         "Rule Explanation": explanation,
#                         "Fuel Type": m["fuel_type"],
#                         "CC Band": m["cc_band"],
#                     })
            
#             print(f"[GEO_NEW_OLD_SATP] Extracted {len(records)} records")
#             return records
            
#         except Exception as e:
#             print(f"[GEO_NEW_OLD_SATP] Error: {e}")
#             traceback.print_exc()
#             return []


# # ===============================================================================
# # SATP CC BAND PROCESSOR
# # ===============================================================================

# class SATPCCProcessor:
#     """Process SATP (Third Party) sheets with CC (Cubic Capacity) bands."""
    
#     @staticmethod
#     def process(content: bytes, sheet_name: str,
#                 override_enabled: bool = False,
#                 override_lob: str = None,
#                 override_segment: str = None) -> List[Dict]:
#         """
#         Process SATP CC Band pattern:
#         Row 1: Title (JAN 2025 PAYOUT - PC TP)
#         Row 2: Geo Locations | SATP Petrol | SATP Diesel
#         Row 3: (empty) | <1000 cc | 1000-1500 cc | >1500 cc | 1000-1500 cc | >1500 cc
#         Row 4+: Data rows
#         """
#         records = []
        
#         try:
#             df = pd.read_excel(io.BytesIO(content), sheet_name=sheet_name, header=None)
            
#             print(f"\n[SATP_CC] Processing sheet: {sheet_name}")
#             print(f"[SATP_CC] Sheet shape: {df.shape}")
            
#             # Find the "Geo Locations" header row
#             header_row = None
#             for i in range(min(10, df.shape[0])):
#                 row_text = cell_to_str(df.iloc[i, 0]).upper()
#                 if "GEO LOCATION" in row_text or "GEO LOC" in row_text:
#                     header_row = i
#                     break
            
#             if header_row is None:
#                 print("[SATP_CC] 'Geo Locations' header row not found")
#                 return records
            
#             print(f"[SATP_CC] Found header row at index: {header_row}")
            
#             # Row structure:
#             # header_row: Geo Locations | SATP Petrol | SATP Diesel
#             # header_row + 1: (empty) | <1000 cc | 1000-1500 cc | >1500 cc | ...
#             cc_row = header_row + 1
            
#             # Data starts after CC row
#             data_start = cc_row + 1
            
#             # Skip empty rows
#             for i in range(data_start, df.shape[0]):
#                 if cell_to_str(df.iloc[i, 0]):
#                     data_start = i
#                     break
            
#             print(f"[SATP_CC] CC row: {cc_row}, Data starts: {data_start}")
            
#             # Build column metadata
#             col_meta = []
#             for col_idx in range(1, df.shape[1]):
#                 fuel_type = cell_to_str(df.iloc[header_row, col_idx]).upper()
#                 cc_band = cell_to_str(df.iloc[cc_row, col_idx])
                
#                 if not fuel_type and not cc_band:
#                     continue
                
#                 # Determine fuel type from header
#                 if "PETROL" in fuel_type:
#                     fuel = "Petrol"
#                 elif "DIESEL" in fuel_type:
#                     fuel = "Diesel"
#                 else:
#                     # Use previous fuel type (for merged cells)
#                     if col_meta:
#                         fuel = col_meta[-1]["fuel_type"]
#                     else:
#                         fuel = "Unknown"
                
#                 # Build segment description
#                 segment_desc = f"SATP {fuel}"
#                 if cc_band:
#                     segment_desc += f" ({cc_band})"
                
#                 col_meta.append({
#                     "col_idx": col_idx,
#                     "fuel_type": fuel,
#                     "cc_band": cc_band,
#                     "segment_desc": segment_desc,
#                 })
            
#             if not col_meta:
#                 print("[SATP_CC] No data columns found")
#                 return records
            
#             print(f"[SATP_CC] Found {len(col_meta)} columns")
#             for m in col_meta:
#                 print(f"  - Col {m['col_idx']}: {m['segment_desc']}")
            
#             # Process data rows
#             lob_final = override_lob if override_enabled and override_lob else "PVT CAR"
#             segment_final = override_segment if override_enabled and override_segment else "PVT CAR TP"
            
#             skip_words = {"total", "grand total", "average", "sum", ""}
            
#             for row_idx in range(data_start, df.shape[0]):
#                 geo_location = cell_to_str(df.iloc[row_idx, 0])
                
#                 if not geo_location or geo_location.lower() in skip_words:
#                     continue
                
#                 state = map_state(geo_location)
                
#                 # Process each column
#                 for m in col_meta:
#                     payin = safe_float(df.iloc[row_idx, m["col_idx"]])
                    
#                     if payin is None or payin == 0:
#                         continue
                    
#                     payout, formula, explanation = calculate_payout(payin, lob_final, segment_final)
                    
#                     records.append({
#                         "State": state,
#                         "Geo Location": geo_location,
#                         "Original Segment": m["segment_desc"],
#                         "Mapped Segment": segment_final,
#                         "LOB": lob_final,
#                         "Policy Type": "TP",
#                         "Status": "STP",
#                         "Payin (OD Premium)": f"{payin:.2f}%",
#                         "Calculated Payout": f"{payout:.2f}%",
#                         "Formula Used": formula,
#                         "Rule Explanation": explanation,
#                         "Fuel Type": m["fuel_type"],
#                         "CC Band": m["cc_band"],
#                     })
            
#             print(f"[SATP_CC] Extracted {len(records)} records")
#             return records
            
#         except Exception as e:
#             print(f"[SATP_CC] Error: {e}")
#             traceback.print_exc()
#             return []


# # ===============================================================================
# # COMP/SAOD PROCESSOR (Original Pattern)
# # ===============================================================================

# class CompSaodProcessor:
#     """Process COMP/SAOD pattern sheets."""
    
#     @staticmethod
#     def process(content: bytes, sheet_name: str,
#                 override_enabled: bool = False,
#                 override_lob: str = None,
#                 override_segment: str = None) -> List[Dict]:
#         """
#         Process Excel sheet with structure:
#         Row 0: Title row (JAN 2025 PAYOUT - PC COMP)
#         Row 1: Main headers (Geo Locations | Payout on | Segment columns)
#         Row 2-3: Empty or sub-headers
#         Row 4+: Data rows
#         """
#         records = []
        
#         try:
#             # Read Excel without header to inspect structure
#             df = pd.read_excel(io.BytesIO(content), sheet_name=sheet_name, header=None)
            
#             print(f"\n[COMP_SAOD] Processing sheet: {sheet_name}")
#             print(f"[COMP_SAOD] Sheet shape: {df.shape}")
            
#             # Find the header row (contains "Geo Locations")
#             header_row = None
#             for i in range(min(10, df.shape[0])):
#                 row_text = " ".join(cell_to_str(v) for v in df.iloc[i]).upper()
#                 if "GEO LOCATION" in row_text or "GEO LOC" in row_text:
#                     header_row = i
#                     break
            
#             if header_row is None:
#                 print("[COMP_SAOD] Could not find 'Geo Locations' header row")
#                 return records
            
#             print(f"[COMP_SAOD] Found header row at index: {header_row}")
            
#             # The actual data starts after header row
#             data_start = header_row + 1
            
#             # Skip any empty rows after header
#             for i in range(data_start, df.shape[0]):
#                 if cell_to_str(df.iloc[i, 0]):  # First column has content
#                     data_start = i
#                     break
            
#             print(f"[COMP_SAOD] Data starts at row: {data_start}")
            
#             # Build column metadata from header row
#             col_meta = []
#             for col_idx in range(2, df.shape[1]):  # Skip column 0 (Geo) and 1 (Payout on)
#                 header = cell_to_str(df.iloc[header_row, col_idx])
                
#                 if not header:
#                     continue
                
#                 # Determine policy type and segment from header
#                 header_upper = header.upper()
                
#                 if "COMP" in header_upper and "SOD" not in header_upper:
#                     policy_type = "COMP"
#                     segment = "PVT CAR COMP + SAOD"
#                 elif "SOD" in header_upper or "SAOD" in header_upper:
#                     policy_type = "SAOD"
#                     segment = "PVT CAR COMP + SAOD"
#                 elif "TP" in header_upper:
#                     policy_type = "TP"
#                     segment = "PVT CAR TP"
#                 else:
#                     policy_type = "COMP"
#                     segment = "PVT CAR COMP + SAOD"
                
#                 col_meta.append({
#                     "col_idx": col_idx,
#                     "header": header,
#                     "policy_type": policy_type,
#                     "segment": segment,
#                 })
            
#             if not col_meta:
#                 print("[COMP_SAOD] No data columns found")
#                 return records
            
#             print(f"[COMP_SAOD] Found {len(col_meta)} data columns")
#             for m in col_meta:
#                 print(f"  - Col {m['col_idx']}: {m['header']} -> {m['policy_type']}")
            
#             # Process data rows
#             lob_final = override_lob if override_enabled and override_lob else "PVT CAR"
            
#             skip_words = {"total", "grand total", "average", "sum", ""}
            
#             for row_idx in range(data_start, df.shape[0]):
#                 geo_location = cell_to_str(df.iloc[row_idx, 0])
                
#                 if not geo_location or geo_location.lower() in skip_words:
#                     continue
                
#                 state = map_state(geo_location)
                
#                 # Process each column
#                 for m in col_meta:
#                     payin = safe_float(df.iloc[row_idx, m["col_idx"]])
                    
#                     if payin is None or payin == 0:
#                         continue
                    
#                     segment_final = override_segment if override_enabled and override_segment else m["segment"]
                    
#                     payout, formula, explanation = calculate_payout(payin, lob_final, segment_final)
                    
#                     records.append({
#                         "State": state,
#                         "Geo Location": geo_location,
#                         "Original Segment": m["header"],
#                         "Mapped Segment": segment_final,
#                         "LOB": lob_final,
#                         "Policy Type": m["policy_type"],
#                         "Status": "STP",
#                         "Payin (OD Premium)": f"{payin:.2f}%",
#                         "Calculated Payout": f"{payout:.2f}%",
#                         "Formula Used": formula,
#                         "Rule Explanation": explanation,
#                     })
            
#             print(f"[COMP_SAOD] Extracted {len(records)} records")
#             return records
            
#         except Exception as e:
#             print(f"[COMP_SAOD] Error: {e}")
#             traceback.print_exc()
#             return []


# # ===============================================================================
# # PATTERN DISPATCHER
# # ===============================================================================

# class PatternDispatcher:
#     """Route to the correct processor based on detected pattern."""
    
#     PATTERN_PROCESSORS = {
#         "comp_saod": CompSaodProcessor,
#         "satp_cc": SATPCCProcessor,
#         "geo_new_old_comp": GeoNewOldCompProcessor,
#         "geo_new_old_satp": GeoNewOldSATPProcessor,
#         "zone_geo_comp": ZoneGeoCompProcessor,
#         "zone_geo_satp": ZoneGeoSATPProcessor,
#     }
    
#     @staticmethod
#     def process_sheet(content: bytes, sheet_name: str,
#                       override_enabled: bool = False,
#                       override_lob: str = None,
#                       override_segment: str = None) -> List[Dict]:
#         """Detect pattern and route to appropriate processor."""
#         # Read raw data to detect pattern
#         df_raw = pd.read_excel(io.BytesIO(content), sheet_name=sheet_name, header=None)
#         pattern = PatternDetector.detect_pattern(df_raw)
        
#         print(f"\n[DISPATCHER] Detected pattern: {pattern}")
        
#         processor_class = PatternDispatcher.PATTERN_PROCESSORS.get(pattern, CompSaodProcessor)
#         return processor_class.process(
#             content, sheet_name,
#             override_enabled, override_lob, override_segment
#         )
#         """
#         Process Excel sheet with structure:
#         Row 0: Title row (JAN 2025 PAYOUT - PC COMP)
#         Row 1: Main headers (Geo Locations | Payout on | Segment columns)
#         Row 2-3: Empty or sub-headers
#         Row 4+: Data rows
#         """
#         records = []
        
#         try:
#             # Read Excel without header to inspect structure
#             df = pd.read_excel(io.BytesIO(content), sheet_name=sheet_name, header=None)
            
#             print(f"\n[PROCESSOR] Processing sheet: {sheet_name}")
#             print(f"[PROCESSOR] Sheet shape: {df.shape}")
            
#             # Find the header row (contains "Geo Locations")
#             header_row = None
#             for i in range(min(10, df.shape[0])):
#                 row_text = " ".join(cell_to_str(v) for v in df.iloc[i]).upper()
#                 if "GEO LOCATION" in row_text or "GEO LOC" in row_text:
#                     header_row = i
#                     break
            
#             if header_row is None:
#                 print("[PROCESSOR] Could not find 'Geo Locations' header row")
#                 return records
            
#             print(f"[PROCESSOR] Found header row at index: {header_row}")
            
#             # The actual data starts after header row
#             data_start = header_row + 1
            
#             # Skip any empty rows after header
#             for i in range(data_start, df.shape[0]):
#                 if cell_to_str(df.iloc[i, 0]):  # First column has content
#                     data_start = i
#                     break
            
#             print(f"[PROCESSOR] Data starts at row: {data_start}")
            
#             # Build column metadata from header row
#             col_meta = []
#             for col_idx in range(2, df.shape[1]):  # Skip column 0 (Geo) and 1 (Payout on)
#                 header = cell_to_str(df.iloc[header_row, col_idx])
                
#                 if not header:
#                     continue
                
#                 # Determine policy type and segment from header
#                 header_upper = header.upper()
                
#                 if "COMP" in header_upper and "SOD" not in header_upper:
#                     policy_type = "COMP"
#                     segment = "PVT CAR COMP + SAOD"
#                 elif "SOD" in header_upper or "SAOD" in header_upper:
#                     policy_type = "SAOD"
#                     segment = "PVT CAR COMP + SAOD"
#                 elif "TP" in header_upper:
#                     policy_type = "TP"
#                     segment = "PVT CAR TP"
#                 else:
#                     policy_type = "COMP"
#                     segment = "PVT CAR COMP + SAOD"
                
#                 col_meta.append({
#                     "col_idx": col_idx,
#                     "header": header,
#                     "policy_type": policy_type,
#                     "segment": segment,
#                 })
            
#             if not col_meta:
#                 print("[PROCESSOR] No data columns found")
#                 return records
            
#             print(f"[PROCESSOR] Found {len(col_meta)} data columns")
#             for m in col_meta:
#                 print(f"  - Col {m['col_idx']}: {m['header']} -> {m['policy_type']}")
            
#             # Process data rows
#             lob_final = override_lob if override_enabled and override_lob else "PVT CAR"
            
#             skip_words = {"total", "grand total", "average", "sum", ""}
            
#             for row_idx in range(data_start, df.shape[0]):
#                 geo_location = cell_to_str(df.iloc[row_idx, 0])
                
#                 if not geo_location or geo_location.lower() in skip_words:
#                     continue
                
#                 state = map_state(geo_location)
                
#                 # Process each column
#                 for m in col_meta:
#                     payin = safe_float(df.iloc[row_idx, m["col_idx"]])
                    
#                     if payin is None or payin == 0:
#                         continue
                    
#                     segment_final = override_segment if override_enabled and override_segment else m["segment"]
                    
#                     payout, formula, explanation = calculate_payout(payin, lob_final, segment_final)
                    
#                     records.append({
#                         "State": state,
#                         "Geo Location": geo_location,
#                         "Original Segment": m["header"],
#                         "Mapped Segment": segment_final,
#                         "LOB": lob_final,
#                         "Policy Type": m["policy_type"],
#                         "Status": "STP",
#                         "Payin (OD Premium)": f"{payin:.2f}%",
#                         "Calculated Payout": f"{payout:.2f}%",
#                         "Formula Used": formula,
#                         "Rule Explanation": explanation,
#                     })
            
#             print(f"[PROCESSOR] Extracted {len(records)} records")
#             return records
            
#         except Exception as e:
#             print(f"[PROCESSOR] Error: {e}")
#             traceback.print_exc()
#             return []


# # ===============================================================================
# # API ENDPOINTS
# # ===============================================================================

# @app.get("/")
# async def root():
#     return {
#         "message": "Insurance Payout Processor API",
#         "version": "4.0.0",
#         "formula": "90% of Payin for all segments",
#         "supported_lobs": ["PVT CAR"],
#         "supported_segments": ["PVT CAR COMP + SAOD", "PVT CAR TP"],
#         "supported_patterns": [
#             "comp_saod - COMP/SAOD with fuel types (Petrol, Diesel, NCB variants)",
#             "satp_cc - SATP (Third Party) with CC bands (<1000cc, 1000-1500cc, >1500cc)",
#             "geo_new_old_comp - COMP with Geo segment New/Old columns",
#             "geo_new_old_satp - SATP with Geo segment New/Old columns",
#             "zone_geo_comp - COMP with Zone + Geo segment Old columns",
#             "zone_geo_satp - SATP with Zone + Geo segment Old columns"
#         ]
#     }


# @app.post("/upload")
# async def upload_file(file: UploadFile = File(...)):
#     """Upload Excel file and return worksheet list."""
#     try:
#         if not file.filename.endswith((".xlsx", ".xls")):
#             raise HTTPException(status_code=400, detail="Only Excel files are supported")
        
#         content = await file.read()
#         xls = pd.ExcelFile(io.BytesIO(content))
#         sheets = xls.sheet_names
        
#         file_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
#         uploaded_files[file_id] = {
#             "content": content,
#             "filename": file.filename,
#             "sheets": sheets,
#         }
        
#         return {
#             "file_id": file_id,
#             "filename": file.filename,
#             "sheets": sheets,
#             "message": f"Uploaded successfully. {len(sheets)} worksheet(s) found.",
#         }
        
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Upload error: {str(e)}")


# @app.post("/process")
# async def process_sheet(
#     file_id: str,
#     sheet_name: str,
#     override_enabled: bool = False,
#     override_lob: Optional[str] = None,
#     override_segment: Optional[str] = None,
# ):
#     """Process a specific worksheet."""
#     try:
#         if file_id not in uploaded_files:
#             raise HTTPException(status_code=404, detail="File not found. Please re-upload.")
        
#         file_data = uploaded_files[file_id]
        
#         if sheet_name not in file_data["sheets"]:
#             raise HTTPException(status_code=400, detail=f"Sheet '{sheet_name}' not found")
        
#         # Use PatternDispatcher to automatically detect and process
#         records = PatternDispatcher.process_sheet(
#             file_data["content"], 
#             sheet_name,
#             override_enabled, 
#             override_lob, 
#             override_segment,
#         )
        
#         if not records:
#             return {
#                 "success": False,
#                 "message": "No records extracted. Check sheet structure.",
#                 "records": [],
#                 "count": 0,
#             }
        
#         # Calculate summary statistics
#         states = {}
#         policies = {}
#         payins = []
#         payouts = []
        
#         for r in records:
#             state = r.get("State", "UNKNOWN")
#             states[state] = states.get(state, 0) + 1
            
#             policy = r.get("Policy Type", "UNKNOWN")
#             policies[policy] = policies.get(policy, 0) + 1
            
#             try:
#                 payin_val = float(r.get("Payin (OD Premium)", "0%").replace("%", ""))
#                 payout_val = float(r.get("Calculated Payout", "0%").replace("%", ""))
#                 payins.append(payin_val)
#                 payouts.append(payout_val)
#             except Exception:
#                 pass
        
#         avg_payin = round(sum(payins) / len(payins), 2) if payins else 0
#         avg_payout = round(sum(payouts) / len(payouts), 2) if payouts else 0
        
#         return {
#             "success": True,
#             "message": f"Successfully processed {len(records)} records from '{sheet_name}'",
#             "records": records,
#             "count": len(records),
#             "summary": {
#                 "total_records": len(records),
#                 "states": dict(sorted(states.items(), key=lambda x: x[1], reverse=True)[:10]),
#                 "policy_types": policies,
#                 "average_payin": avg_payin,
#                 "average_payout": avg_payout,
#             },
#         }
        
#     except Exception as e:
#         traceback.print_exc()
#         raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")


# @app.post("/export")
# async def export_to_excel(file_id: str, sheet_name: str, records: List[Dict]):
#     """Export processed records to Excel."""
#     try:
#         if not records:
#             raise HTTPException(status_code=400, detail="No records to export")
        
#         df = pd.DataFrame(records)
        
#         timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#         filename = f"Processed_{sheet_name.replace(' ', '_')}_{timestamp}.xlsx"
#         out_path = os.path.join(tempfile.gettempdir(), filename)
        
#         # Create Excel writer with formatting
#         with pd.ExcelWriter(out_path, engine='openpyxl') as writer:
#             df.to_excel(writer, index=False, sheet_name="Processed Data")
            
#             # Auto-adjust column widths
#             worksheet = writer.sheets["Processed Data"]
#             for idx, col in enumerate(df.columns):
#                 max_length = max(
#                     df[col].astype(str).apply(len).max(),
#                     len(str(col))
#                 )
#                 worksheet.column_dimensions[chr(65 + idx)].width = min(max_length + 2, 50)
        
#         return FileResponse(
#             path=out_path,
#             filename=filename,
#             media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
#         )
        
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Export error: {str(e)}")


# @app.get("/health")
# async def health_check():
#     """Health check endpoint."""
#     return {
#         "status": "healthy",
#         "timestamp": datetime.now().isoformat(),
#         "uploaded_files": len(uploaded_files)
#     }


# if __name__ == "__main__":
#     import uvicorn
#     print("\n" + "=" * 70)
#     print("Insurance Payout Processor API - v4.0.0")
#     print("Formula: 90% of Payin for all PVT CAR segments")
#     print("Patterns: COMP/SAOD + SATP + Geo New/Old + Zone/Geo")
#     print("=" * 70 + "\n")
#     uvicorn.run(app, host="0.0.0.0", port=8000)



from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
import pandas as pd
import io
import os
from typing import List, Dict, Tuple, Optional
from datetime import datetime
import traceback
import tempfile

app = FastAPI(title="Insurance Payout Processor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===============================================================================
# FORMULA DATA
# ===============================================================================
FORMULA_DATA = [
    {"LOB": "PVT CAR", "SEGMENT": "PVT CAR COMP + SAOD", "PO": "90% of Payin", "REMARKS": "NIL"},
    {"LOB": "PVT CAR", "SEGMENT": "PVT CAR TP", "PO": "90% of Payin", "REMARKS": "NIL"},
]

# ===============================================================================
# STATE MAPPING
# ===============================================================================
STATE_MAPPING = {
    "ANDHRA PRADESH": "ANDHRA PRADESH",
    "KRISHNA": "ANDHRA PRADESH",
    "VIJAYWADA": "ANDHRA PRADESH",
    "VIJAYAWADA": "ANDHRA PRADESH",
    "VISAKHAPATNAM": "ANDHRA PRADESH",
    "VIZAG": "ANDHRA PRADESH",
    
    "KARNATAKA": "KARNATAKA",
    "BANGALORE": "KARNATAKA",
    "BENGALURU": "KARNATAKA",
    "MYSORE": "KARNATAKA",
    "MANGALORE": "KARNATAKA",
    
    "KERALA": "KERALA",
    "ERNAKULAM": "KERALA",
    "COCHIN": "KERALA",
    "KOCHI": "KERALA",
    "TRIVANDRUM": "KERALA",
    "CALICUT": "KERALA",
    "KOZHIKODE": "KERALA",
    
    "TAMIL NADU": "TAMIL NADU",
    "CHENNAI": "TAMIL NADU",
    "MADRAS": "TAMIL NADU",
    "PONDICHERRY": "TAMIL NADU",
    "PUDUCHERRY": "TAMIL NADU",
    "COIMBATORE": "TAMIL NADU",
    "MADURAI": "TAMIL NADU",
    
    "TELANGANA": "TELANGANA",
    "HYDERABAD": "TELANGANA",
    "SECUNDERABAD": "TELANGANA",
    
    "MAHARASHTRA": "MAHARASHTRA",
    "MUMBAI": "MAHARASHTRA",
    "PUNE": "MAHARASHTRA",
    "NAGPUR": "MAHARASHTRA",
    "THANE": "MAHARASHTRA",
    "NASHIK": "MAHARASHTRA",
    
    "DELHI": "DELHI",
    "NEW DELHI": "DELHI",
    "NCR": "DELHI",
    
    "GUJARAT": "GUJARAT",
    "AHMEDABAD": "GUJARAT",
    "SURAT": "GUJARAT",
    "VADODARA": "GUJARAT",
    "RAJKOT": "GUJARAT",
    
    "RAJASTHAN": "RAJASTHAN",
    "JAIPUR": "RAJASTHAN",
    "JODHPUR": "RAJASTHAN",
    "UDAIPUR": "RAJASTHAN",
    
    "UTTAR PRADESH": "UTTAR PRADESH",
    "LUCKNOW": "UTTAR PRADESH",
    "KANPUR": "UTTAR PRADESH",
    "AGRA": "UTTAR PRADESH",
    "VARANASI": "UTTAR PRADESH",
    "NOIDA": "UTTAR PRADESH",
    
    "WEST BENGAL": "WEST BENGAL",
    "KOLKATA": "WEST BENGAL",
    "CALCUTTA": "WEST BENGAL",
    
    "MADHYA PRADESH": "MADHYA PRADESH",
    "BHOPAL": "MADHYA PRADESH",
    "INDORE": "MADHYA PRADESH",
    
    "PUNJAB": "PUNJAB",
    "CHANDIGARH": "CHANDIGARH",
    "HARYANA": "HARYANA",
    "GOA": "GOA",
    "BIHAR": "BIHAR",
    "PATNA": "BIHAR",
    "JHARKHAND": "JHARKHAND",
    "RANCHI": "JHARKHAND",
    "ODISHA": "ODISHA",
    "BHUBANESWAR": "ODISHA",
    "ASSAM": "ASSAM",
    "GUWAHATI": "ASSAM",
}

uploaded_files = {}

# ===============================================================================
# HELPER FUNCTIONS
# ===============================================================================

def cell_to_str(val) -> str:
    """Safely convert ANY cell value (float NaN, None, int, str) to string."""
    if val is None:
        return ""
    try:
        if pd.isna(val):
            return ""
    except (TypeError, ValueError):
        pass
    return str(val).strip()


def safe_float(value) -> Optional[float]:
    """Safely convert value to float, handling percentages and invalid values."""
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    
    s = str(value).strip().upper().replace("%", "")
    if s in ["D", "NA", "", "NAN", "NONE", "DECLINE", "0.00%", "0.0%", "0%"]:
        return None
    
    try:
        num = float(s)
        if num < 0:
            return None
        # Convert decimals to percentages (0.28 -> 28%)
        return num * 100 if 0 < num < 1 else num
    except Exception:
        return None


def map_state(location: str) -> str:
    """Map location/geo name to state using STATE_MAPPING."""
    location_upper = location.upper()
    
    # Direct match first
    for key, val in STATE_MAPPING.items():
        if key.upper() == location_upper:
            return val
    
    # Partial match
    for key, val in STATE_MAPPING.items():
        if key.upper() in location_upper:
            return val
    
    return location  # Return original if no match


def calculate_payout(payin: float, lob: str = "PVT CAR", segment: str = "PVT CAR COMP + SAOD") -> Tuple[float, str, str]:
    """
    Calculate payout based on formula: 90% of Payin
    """
    if payin == 0 or payin is None:
        return 0, "0% (No Payin)", "Payin is 0"
    
    # Formula: 90% of Payin
    payout = round(payin * 0.90, 2)
    formula = "90% of Payin"
    explanation = f"Applied formula: {formula} for {segment}"
    
    return payout, formula, explanation


# ===============================================================================
# PATTERN DETECTION
# ===============================================================================

class PatternDetector:
    """Detect the pattern type of the Excel sheet."""
    
    @staticmethod
    def detect_pattern(df: pd.DataFrame) -> str:
        """
        Detect pattern type:
        - 'comp_saod': COMP/SAOD pattern (Comp - Petrol, SOD - NCB, etc.)
        - 'satp_cc': SATP with CC bands (<1000 cc, 1000-1500 cc, >1500 cc)
        - 'geo_new_old_comp': COMP pattern with Geo segment New/Old columns
        - 'geo_new_old_satp': SATP pattern with Geo segment New/Old columns
        - 'zone_geo_comp': COMP pattern with Zone + Geo segment Old columns
        - 'zone_geo_satp': SATP pattern with Zone + Geo segment Old columns
        """
        # Check first 10 rows for pattern indicators
        sample_text = ""
        for i in range(min(10, df.shape[0])):
            row_text = " ".join(cell_to_str(v) for v in df.iloc[i]).upper()
            sample_text += row_text + " "
        
        # Check for Zone + Geo segment Old pattern
        has_zone = "ZONE" in sample_text and "GEO SEGMENT OLD" in sample_text
        
        if has_zone:
            # Determine if it's COMP or SATP
            if "COMP" in sample_text or "SOD" in sample_text:
                return "zone_geo_comp"
            elif "SATP" in sample_text or "SA TP" in sample_text:
                return "zone_geo_satp"
        
        # Check for Geo segment New/Old pattern (more flexible)
        has_geo_new = "GEO SEGMENT NEW" in sample_text
        has_geo_old = "GEO SEGMENT OLD" in sample_text
        has_both_geos = has_geo_new or (has_geo_old and "GEO SEGMENT" in sample_text)
        
        # Also check for "Final Grid" pattern which has Geo New/Old columns
        has_final_grid = "FINAL GRID" in sample_text
        
        if has_both_geos or has_final_grid:
            # Determine if it's COMP or SATP
            has_comp = "COMP" in sample_text or "SOD" in sample_text or "SAOD" in sample_text
            has_satp = "SATP" in sample_text or "SA TP" in sample_text
            
            if has_satp and not has_comp:
                return "geo_new_old_satp"
            else:
                # Default to COMP for Final Grid and mixed cases
                return "geo_new_old_comp"
        
        # SATP CC Band pattern detection
        if ("SATP" in sample_text or "SA TP" in sample_text) and ("CC" in sample_text or "1000" in sample_text):
            return "satp_cc"
        
        # COMP/SAOD pattern (default)
        return "comp_saod"


# ===============================================================================
# ZONE + GEO OLD COMP PROCESSOR
# ===============================================================================

class ZoneGeoCompProcessor:
    """Process COMP sheets with Zone and Geo segment Old columns."""
    
    @staticmethod
    def process(content: bytes, sheet_name: str,
                override_enabled: bool = False,
                override_lob: str = None,
                override_segment: str = None) -> List[Dict]:
        """
        Process pattern:
        Row 3: Zone | Geo segment Old | Comp - Petrol - NCB / NON NCB | ...
        Row 4+: Data rows (Zone | Geo Old | payin values)
        
        Combined location format: "Zone - Geo segment Old"
        Example: "South - ANDHRA PRADESH - KRISHNA(VIJAYWADA)"
        """
        records = []
        
        try:
            df = pd.read_excel(io.BytesIO(content), sheet_name=sheet_name, header=None)
            
            print(f"\n[ZONE_GEO_COMP] Processing sheet: {sheet_name}")
            print(f"[ZONE_GEO_COMP] Sheet shape: {df.shape}")
            
            # Find header row with "Zone" and "Geo segment Old"
            header_row = None
            for i in range(min(10, df.shape[0])):
                row_text = " ".join(cell_to_str(v) for v in df.iloc[i]).upper()
                if "ZONE" in row_text and "GEO SEGMENT OLD" in row_text:
                    header_row = i
                    break
            
            if header_row is None:
                print("[ZONE_GEO_COMP] Header row not found")
                return records
            
            print(f"[ZONE_GEO_COMP] Found header row at index: {header_row}")
            
            # Data starts after header
            data_start = header_row + 1
            
            # Skip empty rows
            for i in range(data_start, df.shape[0]):
                if cell_to_str(df.iloc[i, 0]) or cell_to_str(df.iloc[i, 1]):
                    data_start = i
                    break
            
            # Build column metadata (starting from column 2, after Zone and Geo Old)
            col_meta = []
            for col_idx in range(2, df.shape[1]):
                header = cell_to_str(df.iloc[header_row, col_idx])
                
                if not header:
                    continue
                
                header_upper = header.upper()
                
                # Determine policy type
                if "COMP" in header_upper and "SOD" not in header_upper and "SAOD" not in header_upper:
                    policy_type = "COMP"
                elif "SOD" in header_upper or "SAOD" in header_upper:
                    policy_type = "SAOD"
                else:
                    policy_type = "COMP"
                
                col_meta.append({
                    "col_idx": col_idx,
                    "header": header,
                    "policy_type": policy_type,
                })
            
            if not col_meta:
                print("[ZONE_GEO_COMP] No data columns found")
                return records
            
            print(f"[ZONE_GEO_COMP] Found {len(col_meta)} columns")
            
            # Process data rows
            lob_final = override_lob if override_enabled and override_lob else "PVT CAR"
            segment_final = override_segment if override_enabled and override_segment else "PVT CAR COMP + SAOD"
            
            skip_words = {"total", "grand total", "average", "sum", ""}
            
            for row_idx in range(data_start, df.shape[0]):
                zone = cell_to_str(df.iloc[row_idx, 0])
                geo_old = cell_to_str(df.iloc[row_idx, 1])
                
                if not geo_old or geo_old.lower() in skip_words:
                    continue
                
                # Combine Zone and Geo Old with hyphen
                combined_location = f"{zone} - {geo_old}" if zone else geo_old
                
                # Extract state from geo_old
                state = map_state(geo_old)
                
                # Process each column
                for m in col_meta:
                    payin = safe_float(df.iloc[row_idx, m["col_idx"]])
                    
                    if payin is None or payin == 0:
                        continue
                    
                    payout, formula, explanation = calculate_payout(payin, lob_final, segment_final)
                    
                    records.append({
                        "State": state,
                        "Geo Location": combined_location,
                        "Zone": zone,
                        "Geo Old": geo_old,
                        "Original Segment": m["header"],
                        "Mapped Segment": segment_final,
                        "LOB": lob_final,
                        "Policy Type": m["policy_type"],
                        "Status": "STP",
                        "Payin (OD Premium)": f"{payin:.2f}%",
                        "Calculated Payout": f"{payout:.2f}%",
                        "Formula Used": formula,
                        "Rule Explanation": explanation,
                    })
            
            print(f"[ZONE_GEO_COMP] Extracted {len(records)} records")
            return records
            
        except Exception as e:
            print(f"[ZONE_GEO_COMP] Error: {e}")
            traceback.print_exc()
            return []


# ===============================================================================
# ZONE + GEO OLD SATP PROCESSOR
# ===============================================================================

class ZoneGeoSATPProcessor:
    """Process SATP sheets with Zone and Geo segment Old columns."""
    
    @staticmethod
    def process(content: bytes, sheet_name: str,
                override_enabled: bool = False,
                override_lob: str = None,
                override_segment: str = None) -> List[Dict]:
        """
        Process pattern:
        Row X: Zone | Geo segment Old | SATP Petrol | SATP Diesel
        Row X+1: (empty) | (empty) | <1000 cc | 1000-1500 cc | >1500 cc | ...
        Row X+2+: Data rows
        """
        records = []
        
        try:
            df = pd.read_excel(io.BytesIO(content), sheet_name=sheet_name, header=None)
            
            print(f"\n[ZONE_GEO_SATP] Processing sheet: {sheet_name}")
            print(f"[ZONE_GEO_SATP] Sheet shape: {df.shape}")
            
            # Find header row with "Zone"
            header_row = None
            for i in range(min(10, df.shape[0])):
                row_text = " ".join(cell_to_str(v) for v in df.iloc[i]).upper()
                if "ZONE" in row_text and ("GEO SEGMENT OLD" in row_text or "SATP" in row_text):
                    header_row = i
                    break
            
            if header_row is None:
                print("[ZONE_GEO_SATP] Header row not found")
                return records
            
            print(f"[ZONE_GEO_SATP] Found header row at index: {header_row}")
            
            # CC band row is next
            cc_row = header_row + 1
            data_start = cc_row + 1
            
            # Build column metadata (starting from column 2)
            col_meta = []
            last_fuel = ""
            
            for col_idx in range(2, df.shape[1]):
                fuel_type = cell_to_str(df.iloc[header_row, col_idx]).upper()
                cc_band = cell_to_str(df.iloc[cc_row, col_idx])
                
                if not fuel_type and not cc_band:
                    continue
                
                # Determine fuel type
                if "PETROL" in fuel_type:
                    last_fuel = "Petrol"
                elif "DIESEL" in fuel_type:
                    last_fuel = "Diesel"
                
                fuel = last_fuel if last_fuel else "Unknown"
                
                # Build segment description
                segment_desc = f"SATP {fuel}"
                if cc_band:
                    segment_desc += f" ({cc_band})"
                
                col_meta.append({
                    "col_idx": col_idx,
                    "fuel_type": fuel,
                    "cc_band": cc_band,
                    "segment_desc": segment_desc,
                })
            
            if not col_meta:
                print("[ZONE_GEO_SATP] No data columns found")
                return records
            
            print(f"[ZONE_GEO_SATP] Found {len(col_meta)} columns")
            
            # Process data rows
            lob_final = override_lob if override_enabled and override_lob else "PVT CAR"
            segment_final = override_segment if override_enabled and override_segment else "PVT CAR TP"
            
            skip_words = {"total", "grand total", "average", "sum", ""}
            
            for row_idx in range(data_start, df.shape[0]):
                zone = cell_to_str(df.iloc[row_idx, 0])
                geo_old = cell_to_str(df.iloc[row_idx, 1])
                
                if not geo_old or geo_old.lower() in skip_words:
                    continue
                
                # Combine Zone and Geo Old with hyphen
                combined_location = f"{zone} - {geo_old}" if zone else geo_old
                
                # Extract state from geo_old
                state = map_state(geo_old)
                
                # Process each column
                for m in col_meta:
                    payin = safe_float(df.iloc[row_idx, m["col_idx"]])
                    
                    if payin is None or payin == 0:
                        continue
                    
                    payout, formula, explanation = calculate_payout(payin, lob_final, segment_final)
                    
                    records.append({
                        "State": state,
                        "Geo Location": combined_location,
                        "Zone": zone,
                        "Geo Old": geo_old,
                        "Original Segment": m["segment_desc"],
                        "Mapped Segment": segment_final,
                        "LOB": lob_final,
                        "Policy Type": "TP",
                        "Status": "STP",
                        "Payin (OD Premium)": f"{payin:.2f}%",
                        "Calculated Payout": f"{payout:.2f}%",
                        "Formula Used": formula,
                        "Rule Explanation": explanation,
                        "Fuel Type": m["fuel_type"],
                        "CC Band": m["cc_band"],
                    })
            
            print(f"[ZONE_GEO_SATP] Extracted {len(records)} records")
            return records
            
        except Exception as e:
            print(f"[ZONE_GEO_SATP] Error: {e}")
            traceback.print_exc()
            return []


# ===============================================================================
# GEO NEW/OLD COMP PROCESSOR
# ===============================================================================

class GeoNewOldCompProcessor:
    """Process COMP sheets with Geo segment New and Geo segment Old columns."""
    
    @staticmethod
    def process(content: bytes, sheet_name: str,
                override_enabled: bool = False,
                override_lob: str = None,
                override_segment: str = None) -> List[Dict]:
        """
        Process pattern:
        Row 1: Title (March 2025 PAYOUT - PCCOMP OR "Final Grid")
        Row 2: Geo segment New | Geo segment Old | Comp - Petrol - NCB / NON NCB | ...
        Row 3+: Data rows
        """
        records = []
        
        try:
            df = pd.read_excel(io.BytesIO(content), sheet_name=sheet_name, header=None)
            
            print(f"\n[GEO_NEW_OLD_COMP] Processing sheet: {sheet_name}")
            print(f"[GEO_NEW_OLD_COMP] Sheet shape: {df.shape}")
            
            # Find header row with "Geo segment New" - check multiple variations
            header_row = None
            for i in range(min(15, df.shape[0])):
                row_text = " ".join(cell_to_str(v) for v in df.iloc[i]).upper()
                if ("GEO SEGMENT NEW" in row_text and "GEO SEGMENT OLD" in row_text) or \
                   ("GEO SEGMENT" in row_text and i < 10):
                    # Double check by looking at the actual cells
                    col0 = cell_to_str(df.iloc[i, 0]).upper()
                    col1 = cell_to_str(df.iloc[i, 1]).upper() if df.shape[1] > 1 else ""
                    
                    if ("GEO" in col0 and "NEW" in col0) or ("GEO" in col1 and "OLD" in col1):
                        header_row = i
                        break
            
            if header_row is None:
                print("[GEO_NEW_OLD_COMP] Header row not found, trying alternate detection")
                # Try to find by looking for "Comp" in later columns
                for i in range(min(15, df.shape[0])):
                    if df.shape[1] > 2:
                        col2 = cell_to_str(df.iloc[i, 2]).upper()
                        col0 = cell_to_str(df.iloc[i, 0]).upper()
                        col1 = cell_to_str(df.iloc[i, 1]).upper()
                        
                        # Check if this looks like a header row
                        if ("COMP" in col2 or "SOD" in col2) and \
                           ("GEO" in col0 or "SEGMENT" in col0 or "ANDHRA" not in col0):
                            header_row = i
                            print(f"[GEO_NEW_OLD_COMP] Found header by COMP detection at row {i}")
                            break
            
            if header_row is None:
                print("[GEO_NEW_OLD_COMP] Still no header row found")
                return records
            
            print(f"[GEO_NEW_OLD_COMP] Found header row at index: {header_row}")
            
            # Data starts after header
            data_start = header_row + 1
            
            # Skip empty rows after header
            for i in range(data_start, df.shape[0]):
                if cell_to_str(df.iloc[i, 0]) or cell_to_str(df.iloc[i, 1]):
                    # Make sure it's not another header row
                    test = cell_to_str(df.iloc[i, 0]).upper()
                    if "GEO" not in test and "SEGMENT" not in test:
                        data_start = i
                        break
            
            print(f"[GEO_NEW_OLD_COMP] Data starts at row: {data_start}")
            
            # Build column metadata (starting from column 2, after Geo New and Geo Old)
            col_meta = []
            for col_idx in range(2, df.shape[1]):
                header = cell_to_str(df.iloc[header_row, col_idx])
                
                if not header:
                    continue
                
                header_upper = header.upper()
                
                # Determine policy type
                if "COMP" in header_upper and "SOD" not in header_upper and "SAOD" not in header_upper:
                    policy_type = "COMP"
                elif "SOD" in header_upper or "SAOD" in header_upper:
                    policy_type = "SAOD"
                else:
                    # Skip columns that don't look like policy columns
                    if not any(x in header_upper for x in ["PETROL", "DIESEL", "NCB", "NON NCB", "OTHERS"]):
                        continue
                    policy_type = "COMP"
                
                col_meta.append({
                    "col_idx": col_idx,
                    "header": header,
                    "policy_type": policy_type,
                })
            
            if not col_meta:
                print("[GEO_NEW_OLD_COMP] No data columns found")
                print(f"[GEO_NEW_OLD_COMP] Header row content: {[cell_to_str(df.iloc[header_row, i]) for i in range(min(10, df.shape[1]))]}")
                return records
            
            print(f"[GEO_NEW_OLD_COMP] Found {len(col_meta)} columns")
            for m in col_meta[:5]:  # Print first 5
                print(f"  - Col {m['col_idx']}: {m['header']} -> {m['policy_type']}")
            
            # Process data rows
            lob_final = override_lob if override_enabled and override_lob else "PVT CAR"
            segment_final = override_segment if override_enabled and override_segment else "PVT CAR COMP + SAOD"
            
            skip_words = {"total", "grand total", "average", "sum", ""}
            
            processed_count = 0
            for row_idx in range(data_start, df.shape[0]):
                geo_new = cell_to_str(df.iloc[row_idx, 0])
                geo_old = cell_to_str(df.iloc[row_idx, 1])
                
                # More lenient checking - if either column has data
                if not geo_new and not geo_old:
                    continue
                    
                if geo_new.lower() in skip_words and geo_old.lower() in skip_words:
                    continue
                
                # Use whichever is available
                if not geo_new:
                    geo_new = geo_old
                if not geo_old:
                    geo_old = geo_new
                
                # Combine Geo New and Geo Old with hyphen
                combined_location = f"{geo_new} - {geo_old}" if geo_new != geo_old else geo_new
                
                # Extract state from geo_old (more specific)
                state = map_state(geo_old if geo_old else geo_new)
                
                # Process each column
                for m in col_meta:
                    payin = safe_float(df.iloc[row_idx, m["col_idx"]])
                    
                    if payin is None or payin == 0:
                        continue
                    
                    payout, formula, explanation = calculate_payout(payin, lob_final, segment_final)
                    
                    records.append({
                        "State": state,
                        "Geo Location": combined_location,
                        "Geo New": geo_new,
                        "Geo Old": geo_old,
                        "Original Segment": m["header"],
                        "Mapped Segment": segment_final,
                        "LOB": lob_final,
                        "Policy Type": m["policy_type"],
                        "Status": "STP",
                        "Payin (OD Premium)": f"{payin:.2f}%",
                        "Calculated Payout": f"{payout:.2f}%",
                        "Formula Used": formula,
                        "Rule Explanation": explanation,
                    })
                    processed_count += 1
            
            print(f"[GEO_NEW_OLD_COMP] Extracted {len(records)} records from {processed_count} data points")
            return records
            
        except Exception as e:
            print(f"[GEO_NEW_OLD_COMP] Error: {e}")
            traceback.print_exc()
            return []


# ===============================================================================
# GEO NEW/OLD SATP PROCESSOR
# ===============================================================================

class GeoNewOldSATPProcessor:
    """Process SATP sheets with Geo segment New and Geo segment Old columns."""
    
    @staticmethod
    def process(content: bytes, sheet_name: str,
                override_enabled: bool = False,
                override_lob: str = None,
                override_segment: str = None) -> List[Dict]:
        """
        Process pattern:
        Row 1: Title (March 2025 PAYOUT - PCSATP)
        Row 2: Geo segment New | Geo segment Old | SATP Petrol | SATP Diesel
        Row 3: (empty) | (empty) | <1000 cc | 1000-1500 cc | >1500 cc | ...
        Row 4+: Data rows
        """
        records = []
        
        try:
            df = pd.read_excel(io.BytesIO(content), sheet_name=sheet_name, header=None)
            
            print(f"\n[GEO_NEW_OLD_SATP] Processing sheet: {sheet_name}")
            print(f"[GEO_NEW_OLD_SATP] Sheet shape: {df.shape}")
            
            # Find header row with "Geo segment New"
            header_row = None
            for i in range(min(10, df.shape[0])):
                row_text = " ".join(cell_to_str(v) for v in df.iloc[i]).upper()
                if "GEO SEGMENT NEW" in row_text:
                    header_row = i
                    break
            
            if header_row is None:
                print("[GEO_NEW_OLD_SATP] Header row not found")
                return records
            
            print(f"[GEO_NEW_OLD_SATP] Found header row at index: {header_row}")
            
            # CC band row is next
            cc_row = header_row + 1
            data_start = cc_row + 1
            
            # Build column metadata (starting from column 2)
            col_meta = []
            last_fuel = ""
            
            for col_idx in range(2, df.shape[1]):
                fuel_type = cell_to_str(df.iloc[header_row, col_idx]).upper()
                cc_band = cell_to_str(df.iloc[cc_row, col_idx])
                
                if not fuel_type and not cc_band:
                    continue
                
                # Determine fuel type
                if "PETROL" in fuel_type:
                    last_fuel = "Petrol"
                elif "DIESEL" in fuel_type:
                    last_fuel = "Diesel"
                
                fuel = last_fuel if last_fuel else "Unknown"
                
                # Build segment description
                segment_desc = f"SATP {fuel}"
                if cc_band:
                    segment_desc += f" ({cc_band})"
                
                col_meta.append({
                    "col_idx": col_idx,
                    "fuel_type": fuel,
                    "cc_band": cc_band,
                    "segment_desc": segment_desc,
                })
            
            if not col_meta:
                print("[GEO_NEW_OLD_SATP] No data columns found")
                return records
            
            print(f"[GEO_NEW_OLD_SATP] Found {len(col_meta)} columns")
            
            # Process data rows
            lob_final = override_lob if override_enabled and override_lob else "PVT CAR"
            segment_final = override_segment if override_enabled and override_segment else "PVT CAR TP"
            
            skip_words = {"total", "grand total", "average", "sum", ""}
            
            for row_idx in range(data_start, df.shape[0]):
                geo_new = cell_to_str(df.iloc[row_idx, 0])
                geo_old = cell_to_str(df.iloc[row_idx, 1])
                
                if not geo_new or geo_new.lower() in skip_words:
                    continue
                
                # Combine Geo New and Geo Old with hyphen
                combined_location = f"{geo_new} - {geo_old}" if geo_old else geo_new
                
                # Extract state from geo_old
                state = map_state(geo_old if geo_old else geo_new)
                
                # Process each column
                for m in col_meta:
                    payin = safe_float(df.iloc[row_idx, m["col_idx"]])
                    
                    if payin is None or payin == 0:
                        continue
                    
                    payout, formula, explanation = calculate_payout(payin, lob_final, segment_final)
                    
                    records.append({
                        "State": state,
                        "Geo Location": combined_location,
                        "Geo New": geo_new,
                        "Geo Old": geo_old,
                        "Original Segment": m["segment_desc"],
                        "Mapped Segment": segment_final,
                        "LOB": lob_final,
                        "Policy Type": "TP",
                        "Status": "STP",
                        "Payin (OD Premium)": f"{payin:.2f}%",
                        "Calculated Payout": f"{payout:.2f}%",
                        "Formula Used": formula,
                        "Rule Explanation": explanation,
                        "Fuel Type": m["fuel_type"],
                        "CC Band": m["cc_band"],
                    })
            
            print(f"[GEO_NEW_OLD_SATP] Extracted {len(records)} records")
            return records
            
        except Exception as e:
            print(f"[GEO_NEW_OLD_SATP] Error: {e}")
            traceback.print_exc()
            return []


# ===============================================================================
# SATP CC BAND PROCESSOR
# ===============================================================================

class SATPCCProcessor:
    """Process SATP (Third Party) sheets with CC (Cubic Capacity) bands."""
    
    @staticmethod
    def process(content: bytes, sheet_name: str,
                override_enabled: bool = False,
                override_lob: str = None,
                override_segment: str = None) -> List[Dict]:
        """
        Process SATP CC Band pattern:
        Row 1: Title (JAN 2025 PAYOUT - PC TP)
        Row 2: Geo Locations | SATP Petrol | SATP Diesel
        Row 3: (empty) | <1000 cc | 1000-1500 cc | >1500 cc | 1000-1500 cc | >1500 cc
        Row 4+: Data rows
        """
        records = []
        
        try:
            df = pd.read_excel(io.BytesIO(content), sheet_name=sheet_name, header=None)
            
            print(f"\n[SATP_CC] Processing sheet: {sheet_name}")
            print(f"[SATP_CC] Sheet shape: {df.shape}")
            
            # Find the "Geo Locations" header row
            header_row = None
            for i in range(min(10, df.shape[0])):
                row_text = cell_to_str(df.iloc[i, 0]).upper()
                if "GEO LOCATION" in row_text or "GEO LOC" in row_text:
                    header_row = i
                    break
            
            if header_row is None:
                print("[SATP_CC] 'Geo Locations' header row not found")
                return records
            
            print(f"[SATP_CC] Found header row at index: {header_row}")
            
            # Row structure:
            # header_row: Geo Locations | SATP Petrol | SATP Diesel
            # header_row + 1: (empty) | <1000 cc | 1000-1500 cc | >1500 cc | ...
            cc_row = header_row + 1
            
            # Data starts after CC row
            data_start = cc_row + 1
            
            # Skip empty rows
            for i in range(data_start, df.shape[0]):
                if cell_to_str(df.iloc[i, 0]):
                    data_start = i
                    break
            
            print(f"[SATP_CC] CC row: {cc_row}, Data starts: {data_start}")
            
            # Build column metadata
            col_meta = []
            for col_idx in range(1, df.shape[1]):
                fuel_type = cell_to_str(df.iloc[header_row, col_idx]).upper()
                cc_band = cell_to_str(df.iloc[cc_row, col_idx])
                
                if not fuel_type and not cc_band:
                    continue
                
                # Determine fuel type from header
                if "PETROL" in fuel_type:
                    fuel = "Petrol"
                elif "DIESEL" in fuel_type:
                    fuel = "Diesel"
                else:
                    # Use previous fuel type (for merged cells)
                    if col_meta:
                        fuel = col_meta[-1]["fuel_type"]
                    else:
                        fuel = "Unknown"
                
                # Build segment description
                segment_desc = f"SATP {fuel}"
                if cc_band:
                    segment_desc += f" ({cc_band})"
                
                col_meta.append({
                    "col_idx": col_idx,
                    "fuel_type": fuel,
                    "cc_band": cc_band,
                    "segment_desc": segment_desc,
                })
            
            if not col_meta:
                print("[SATP_CC] No data columns found")
                return records
            
            print(f"[SATP_CC] Found {len(col_meta)} columns")
            for m in col_meta:
                print(f"  - Col {m['col_idx']}: {m['segment_desc']}")
            
            # Process data rows
            lob_final = override_lob if override_enabled and override_lob else "PVT CAR"
            segment_final = override_segment if override_enabled and override_segment else "PVT CAR TP"
            
            skip_words = {"total", "grand total", "average", "sum", ""}
            
            for row_idx in range(data_start, df.shape[0]):
                geo_location = cell_to_str(df.iloc[row_idx, 0])
                
                if not geo_location or geo_location.lower() in skip_words:
                    continue
                
                state = map_state(geo_location)
                
                # Process each column
                for m in col_meta:
                    payin = safe_float(df.iloc[row_idx, m["col_idx"]])
                    
                    if payin is None or payin == 0:
                        continue
                    
                    payout, formula, explanation = calculate_payout(payin, lob_final, segment_final)
                    
                    records.append({
                        "State": state,
                        "Geo Location": geo_location,
                        "Original Segment": m["segment_desc"],
                        "Mapped Segment": segment_final,
                        "LOB": lob_final,
                        "Policy Type": "TP",
                        "Status": "STP",
                        "Payin (OD Premium)": f"{payin:.2f}%",
                        "Calculated Payout": f"{payout:.2f}%",
                        "Formula Used": formula,
                        "Rule Explanation": explanation,
                        "Fuel Type": m["fuel_type"],
                        "CC Band": m["cc_band"],
                    })
            
            print(f"[SATP_CC] Extracted {len(records)} records")
            return records
            
        except Exception as e:
            print(f"[SATP_CC] Error: {e}")
            traceback.print_exc()
            return []


# ===============================================================================
# COMP/SAOD PROCESSOR (Original Pattern)
# ===============================================================================

class CompSaodProcessor:
    """Process COMP/SAOD pattern sheets."""
    
    @staticmethod
    def process(content: bytes, sheet_name: str,
                override_enabled: bool = False,
                override_lob: str = None,
                override_segment: str = None) -> List[Dict]:
        """
        Process Excel sheet with structure:
        Row 0: Title row (JAN 2025 PAYOUT - PC COMP)
        Row 1: Main headers (Geo Locations | Payout on | Segment columns)
        Row 2-3: Empty or sub-headers
        Row 4+: Data rows
        """
        records = []
        
        try:
            # Read Excel without header to inspect structure
            df = pd.read_excel(io.BytesIO(content), sheet_name=sheet_name, header=None)
            
            print(f"\n[COMP_SAOD] Processing sheet: {sheet_name}")
            print(f"[COMP_SAOD] Sheet shape: {df.shape}")
            
            # Find the header row (contains "Geo Locations")
            header_row = None
            for i in range(min(10, df.shape[0])):
                row_text = " ".join(cell_to_str(v) for v in df.iloc[i]).upper()
                if "GEO LOCATION" in row_text or "GEO LOC" in row_text:
                    header_row = i
                    break
            
            if header_row is None:
                print("[COMP_SAOD] Could not find 'Geo Locations' header row")
                return records
            
            print(f"[COMP_SAOD] Found header row at index: {header_row}")
            
            # The actual data starts after header row
            data_start = header_row + 1
            
            # Skip any empty rows after header
            for i in range(data_start, df.shape[0]):
                if cell_to_str(df.iloc[i, 0]):  # First column has content
                    data_start = i
                    break
            
            print(f"[COMP_SAOD] Data starts at row: {data_start}")
            
            # Build column metadata from header row
            col_meta = []
            for col_idx in range(2, df.shape[1]):  # Skip column 0 (Geo) and 1 (Payout on)
                header = cell_to_str(df.iloc[header_row, col_idx])
                
                if not header:
                    continue
                
                # Determine policy type and segment from header
                header_upper = header.upper()
                
                if "COMP" in header_upper and "SOD" not in header_upper:
                    policy_type = "COMP"
                    segment = "PVT CAR COMP + SAOD"
                elif "SOD" in header_upper or "SAOD" in header_upper:
                    policy_type = "SAOD"
                    segment = "PVT CAR COMP + SAOD"
                elif "TP" in header_upper:
                    policy_type = "TP"
                    segment = "PVT CAR TP"
                else:
                    policy_type = "COMP"
                    segment = "PVT CAR COMP + SAOD"
                
                col_meta.append({
                    "col_idx": col_idx,
                    "header": header,
                    "policy_type": policy_type,
                    "segment": segment,
                })
            
            if not col_meta:
                print("[COMP_SAOD] No data columns found")
                return records
            
            print(f"[COMP_SAOD] Found {len(col_meta)} data columns")
            for m in col_meta:
                print(f"  - Col {m['col_idx']}: {m['header']} -> {m['policy_type']}")
            
            # Process data rows
            lob_final = override_lob if override_enabled and override_lob else "PVT CAR"
            
            skip_words = {"total", "grand total", "average", "sum", ""}
            
            for row_idx in range(data_start, df.shape[0]):
                geo_location = cell_to_str(df.iloc[row_idx, 0])
                
                if not geo_location or geo_location.lower() in skip_words:
                    continue
                
                state = map_state(geo_location)
                
                # Process each column
                for m in col_meta:
                    payin = safe_float(df.iloc[row_idx, m["col_idx"]])
                    
                    if payin is None or payin == 0:
                        continue
                    
                    segment_final = override_segment if override_enabled and override_segment else m["segment"]
                    
                    payout, formula, explanation = calculate_payout(payin, lob_final, segment_final)
                    
                    records.append({
                        "State": state,
                        "Geo Location": geo_location,
                        "Original Segment": m["header"],
                        "Mapped Segment": segment_final,
                        "LOB": lob_final,
                        "Policy Type": m["policy_type"],
                        "Status": "STP",
                        "Payin (OD Premium)": f"{payin:.2f}%",
                        "Calculated Payout": f"{payout:.2f}%",
                        "Formula Used": formula,
                        "Rule Explanation": explanation,
                    })
            
            print(f"[COMP_SAOD] Extracted {len(records)} records")
            return records
            
        except Exception as e:
            print(f"[COMP_SAOD] Error: {e}")
            traceback.print_exc()
            return []


# ===============================================================================
# PATTERN DISPATCHER
# ===============================================================================

class PatternDispatcher:
    """Route to the correct processor based on detected pattern."""
    
    PATTERN_PROCESSORS = {
        "comp_saod": CompSaodProcessor,
        "satp_cc": SATPCCProcessor,
        "geo_new_old_comp": GeoNewOldCompProcessor,
        "geo_new_old_satp": GeoNewOldSATPProcessor,
        "zone_geo_comp": ZoneGeoCompProcessor,
        "zone_geo_satp": ZoneGeoSATPProcessor,
    }
    
    @staticmethod
    def process_sheet(content: bytes, sheet_name: str,
                      override_enabled: bool = False,
                      override_lob: str = None,
                      override_segment: str = None) -> List[Dict]:
        """Detect pattern and route to appropriate processor."""
        # Read raw data to detect pattern
        df_raw = pd.read_excel(io.BytesIO(content), sheet_name=sheet_name, header=None)
        pattern = PatternDetector.detect_pattern(df_raw)
        
        print(f"\n[DISPATCHER] Detected pattern: {pattern}")
        
        processor_class = PatternDispatcher.PATTERN_PROCESSORS.get(pattern, CompSaodProcessor)
        return processor_class.process(
            content, sheet_name,
            override_enabled, override_lob, override_segment
        )
        """
        Process Excel sheet with structure:
        Row 0: Title row (JAN 2025 PAYOUT - PC COMP)
        Row 1: Main headers (Geo Locations | Payout on | Segment columns)
        Row 2-3: Empty or sub-headers
        Row 4+: Data rows
        """
        records = []
        
        try:
            # Read Excel without header to inspect structure
            df = pd.read_excel(io.BytesIO(content), sheet_name=sheet_name, header=None)
            
            print(f"\n[PROCESSOR] Processing sheet: {sheet_name}")
            print(f"[PROCESSOR] Sheet shape: {df.shape}")
            
            # Find the header row (contains "Geo Locations")
            header_row = None
            for i in range(min(10, df.shape[0])):
                row_text = " ".join(cell_to_str(v) for v in df.iloc[i]).upper()
                if "GEO LOCATION" in row_text or "GEO LOC" in row_text:
                    header_row = i
                    break
            
            if header_row is None:
                print("[PROCESSOR] Could not find 'Geo Locations' header row")
                return records
            
            print(f"[PROCESSOR] Found header row at index: {header_row}")
            
            # The actual data starts after header row
            data_start = header_row + 1
            
            # Skip any empty rows after header
            for i in range(data_start, df.shape[0]):
                if cell_to_str(df.iloc[i, 0]):  # First column has content
                    data_start = i
                    break
            
            print(f"[PROCESSOR] Data starts at row: {data_start}")
            
            # Build column metadata from header row
            col_meta = []
            for col_idx in range(2, df.shape[1]):  # Skip column 0 (Geo) and 1 (Payout on)
                header = cell_to_str(df.iloc[header_row, col_idx])
                
                if not header:
                    continue
                
                # Determine policy type and segment from header
                header_upper = header.upper()
                
                if "COMP" in header_upper and "SOD" not in header_upper:
                    policy_type = "COMP"
                    segment = "PVT CAR COMP + SAOD"
                elif "SOD" in header_upper or "SAOD" in header_upper:
                    policy_type = "SAOD"
                    segment = "PVT CAR COMP + SAOD"
                elif "TP" in header_upper:
                    policy_type = "TP"
                    segment = "PVT CAR TP"
                else:
                    policy_type = "COMP"
                    segment = "PVT CAR COMP + SAOD"
                
                col_meta.append({
                    "col_idx": col_idx,
                    "header": header,
                    "policy_type": policy_type,
                    "segment": segment,
                })
            
            if not col_meta:
                print("[PROCESSOR] No data columns found")
                return records
            
            print(f"[PROCESSOR] Found {len(col_meta)} data columns")
            for m in col_meta:
                print(f"  - Col {m['col_idx']}: {m['header']} -> {m['policy_type']}")
            
            # Process data rows
            lob_final = override_lob if override_enabled and override_lob else "PVT CAR"
            
            skip_words = {"total", "grand total", "average", "sum", ""}
            
            for row_idx in range(data_start, df.shape[0]):
                geo_location = cell_to_str(df.iloc[row_idx, 0])
                
                if not geo_location or geo_location.lower() in skip_words:
                    continue
                
                state = map_state(geo_location)
                
                # Process each column
                for m in col_meta:
                    payin = safe_float(df.iloc[row_idx, m["col_idx"]])
                    
                    if payin is None or payin == 0:
                        continue
                    
                    segment_final = override_segment if override_enabled and override_segment else m["segment"]
                    
                    payout, formula, explanation = calculate_payout(payin, lob_final, segment_final)
                    
                    records.append({
                        "State": state,
                        "Geo Location": geo_location,
                        "Original Segment": m["header"],
                        "Mapped Segment": segment_final,
                        "LOB": lob_final,
                        "Policy Type": m["policy_type"],
                        "Status": "STP",
                        "Payin (OD Premium)": f"{payin:.2f}%",
                        "Calculated Payout": f"{payout:.2f}%",
                        "Formula Used": formula,
                        "Rule Explanation": explanation,
                    })
            
            print(f"[PROCESSOR] Extracted {len(records)} records")
            return records
            
        except Exception as e:
            print(f"[PROCESSOR] Error: {e}")
            traceback.print_exc()
            return []


# ===============================================================================
# API ENDPOINTS
# ===============================================================================

@app.get("/")
async def root():
    return {
        "message": "Insurance Payout Processor API",
        "version": "4.0.0",
        "formula": "90% of Payin for all segments",
        "supported_lobs": ["PVT CAR"],
        "supported_segments": ["PVT CAR COMP + SAOD", "PVT CAR TP"],
        "supported_patterns": [
            "comp_saod - COMP/SAOD with fuel types (Petrol, Diesel, NCB variants)",
            "satp_cc - SATP (Third Party) with CC bands (<1000cc, 1000-1500cc, >1500cc)",
            "geo_new_old_comp - COMP with Geo segment New/Old columns",
            "geo_new_old_satp - SATP with Geo segment New/Old columns",
            "zone_geo_comp - COMP with Zone + Geo segment Old columns",
            "zone_geo_satp - SATP with Zone + Geo segment Old columns"
        ]
    }


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload Excel file and return worksheet list."""
    try:
        if not file.filename.endswith((".xlsx", ".xls")):
            raise HTTPException(status_code=400, detail="Only Excel files are supported")
        
        content = await file.read()
        xls = pd.ExcelFile(io.BytesIO(content))
        sheets = xls.sheet_names
        
        file_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        uploaded_files[file_id] = {
            "content": content,
            "filename": file.filename,
            "sheets": sheets,
        }
        
        return {
            "file_id": file_id,
            "filename": file.filename,
            "sheets": sheets,
            "message": f"Uploaded successfully. {len(sheets)} worksheet(s) found.",
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload error: {str(e)}")


@app.post("/process")
async def process_sheet(
    file_id: str,
    sheet_name: str,
    override_enabled: bool = False,
    override_lob: Optional[str] = None,
    override_segment: Optional[str] = None,
):
    """Process a specific worksheet."""
    try:
        if file_id not in uploaded_files:
            raise HTTPException(status_code=404, detail="File not found. Please re-upload.")
        
        file_data = uploaded_files[file_id]
        
        if sheet_name not in file_data["sheets"]:
            raise HTTPException(status_code=400, detail=f"Sheet '{sheet_name}' not found")
        
        # Use PatternDispatcher to automatically detect and process
        records = PatternDispatcher.process_sheet(
            file_data["content"], 
            sheet_name,
            override_enabled, 
            override_lob, 
            override_segment,
        )
        
        if not records:
            return {
                "success": False,
                "message": "No records extracted. Check sheet structure.",
                "records": [],
                "count": 0,
            }
        
        # Calculate summary statistics
        states = {}
        policies = {}
        payins = []
        payouts = []
        
        for r in records:
            state = r.get("State", "UNKNOWN")
            states[state] = states.get(state, 0) + 1
            
            policy = r.get("Policy Type", "UNKNOWN")
            policies[policy] = policies.get(policy, 0) + 1
            
            try:
                payin_val = float(r.get("Payin (OD Premium)", "0%").replace("%", ""))
                payout_val = float(r.get("Calculated Payout", "0%").replace("%", ""))
                payins.append(payin_val)
                payouts.append(payout_val)
            except Exception:
                pass
        
        avg_payin = round(sum(payins) / len(payins), 2) if payins else 0
        avg_payout = round(sum(payouts) / len(payouts), 2) if payouts else 0
        
        return {
            "success": True,
            "message": f"Successfully processed {len(records)} records from '{sheet_name}'",
            "records": records,
            "count": len(records),
            "summary": {
                "total_records": len(records),
                "states": dict(sorted(states.items(), key=lambda x: x[1], reverse=True)[:10]),
                "policy_types": policies,
                "average_payin": avg_payin,
                "average_payout": avg_payout,
            },
        }
        
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")


@app.post("/export")
async def export_to_excel(file_id: str, sheet_name: str, records: List[Dict]):
    """Export processed records to Excel."""
    try:
        if not records:
            raise HTTPException(status_code=400, detail="No records to export")
        
        df = pd.DataFrame(records)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"Processed_{sheet_name.replace(' ', '_')}_{timestamp}.xlsx"
        out_path = os.path.join(tempfile.gettempdir(), filename)
        
        # Create Excel writer with formatting
        with pd.ExcelWriter(out_path, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name="Processed Data")
            
            # Auto-adjust column widths
            worksheet = writer.sheets["Processed Data"]
            for idx, col in enumerate(df.columns):
                max_length = max(
                    df[col].astype(str).apply(len).max(),
                    len(str(col))
                )
                worksheet.column_dimensions[chr(65 + idx)].width = min(max_length + 2, 50)
        
        return FileResponse(
            path=out_path,
            filename=filename,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export error: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "uploaded_files": len(uploaded_files)
    }


if __name__ == "__main__":
    import uvicorn
    print("\n" + "=" * 70)
    print("Insurance Payout Processor API - v4.0.0")
    print("Formula: 90% of Payin for all PVT CAR segments")
    print("Patterns: COMP/SAOD + SATP + Geo New/Old + Zone/Geo")
    print("=" * 70 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)
