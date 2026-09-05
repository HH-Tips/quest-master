# QuestMaster: Progetto Finale su Agentic AI

**Scadenza:** 30 settembre 2025, ore 23:59

---

## Introduzione

**QuestMaster** è un sistema a due fasi progettato per aiutare gli autori a creare esperienze narrative interattive attraverso tecniche di pianificazione classica (**PDDL**) e intelligenza artificiale generativa (**LLM**). Il sistema si divide in:

1. **Story Generation Phase** (Fase 1)
2. **Interactive Story Game Phase** (Fase 2)

---

## Fase 1: Story Generation

### Obiettivo

Assistere gli autori in modo interattivo nella creazione di una *quest* narrativa logicamente coerente, rappresentata come un problema di pianificazione PDDL.

### Input

Un **Lore Document** contenente i seguenti elementi:

* **Quest Description:** Descrizione dell'avventura (stato iniziale, obiettivo, ostacoli) e contesto del mondo di gioco.
* **Branching Factor:** Numero minimo e massimo di azioni disponibili in ogni stato narrativo.
* **Depth Constraints:** Numero minimo e massimo di passaggi per raggiungere l'obiettivo.

### Workflow

1. **Generazione e Validazione PDDL:**
* Il sistema produce un file PDDL che modella l'avventura. Ogni riga di codice è accompagnata da un commento descrittivo.
* Viene utilizzato un pianificatore classico (es. *Fast Downward*) per verificare la presenza di almeno un percorso valido verso l'obiettivo.


2. **Interactive Refinement Loop (in caso di modello non valido):**
* Se non esiste una soluzione, un **Reflection Agent** (LLM) identifica le incongruenze logiche.
* L'agente suggerisce modifiche e interagisce con l'autore tramite chat per ottenere approvazione o ulteriori input.



### Output Fase 1

* File PDDL (Domain e Problem) completi e validati.
* Lore file finalizzato (aggiornato in base alla versione finale del PDDL).

---

## Fase 2: Interactive Story Game

### Obiettivo

Creare un'esperienza narrativa interattiva basata sul web utilizzando i file generati nella Fase 1.

### Workflow

1. **Generazione HTML:**
* Un agente LLM genera un'implementazione HTML interattiva dell'avventura.
* *Opzionale:* Generazione di immagini specifiche per ogni stato per rappresentare il contesto narrativo e le scelte.



---

## Materiale da consegnare

* **Project Files:** Archivio `.zip` con il codice implementato.
* **Esempio di Quest:** Documento di Lore iniziale e file di output (PDDL e HTML).
