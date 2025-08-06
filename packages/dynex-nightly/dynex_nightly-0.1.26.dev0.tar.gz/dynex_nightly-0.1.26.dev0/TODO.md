# DYNEX refactoring roadmap

## 🏗️ Core Architecture
- [ ] Implement API validation using interfaces  
- [x] Split `init.py` into logical modules  
- [x] Create dedicated **API module**  
- [x] Create dedicated **Sampler module**  
- [ ] Move model-related code to `models.py`  
- [ ] Extract reusable utilities to `utils.py`  
- [ ] Local files

## ⚙️ Configuration & Maintenance
- [x] Design a unified config system (library-wide)  
- [ ] Improve solver version management   
- [ ] Improve solver location management   
- [ ] Remove local file storage where possible (use in-memory/cloud alternatives)

## 🔍 Testing & Validation
- [x] Test BQM model functionality  
- [x] Test SAT model functionality  
- [x] Test CQM model functionality  
- [ ] Test DQM model functionality  
- [ ] Implement smoke test  

## 🧩 Dynex Circuit Refactor
- [ ] Split `dynex_circuit` into logical components  
- [ ] Refactor `dynex_circuit` into classes  

## 🛠️ Code Quality & Standards
- [ ] Adopt OOP and Python best practices  
- [ ] Apply **PEP 8** (style), **PEP 484** (type hints), **PEP 257** (docstrings)  
- [x] Replace `print()` with `logging` module  
- [ ] Add a linter (e.g., `flake8`, `pylint`)  
- [ ] Implement unified exception handling  
