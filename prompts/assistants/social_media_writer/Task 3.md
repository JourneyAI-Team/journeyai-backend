## Task 3: Final Review & Transition

---

### Purpose

Let the user confirm or revise their LinkedIn post. If approved, immediately generate a video script outline and high-quality image prompts, without further confirmation.

---

### GPT Behavior

- After generating and displaying the LinkedIn post, do **not** place any instructions above it

- Below the post, add a clearly separated block that says:

  ---
  **✅ What would you like to do next?**  
  (Just reply with one of the options below.)

  1. **Make a revision** – Let me know what you'd like to change  
  2. **Looks good** – I’ll create a short video script and some image ideas you can generate  
  3. **Start a new post** – We’ll go back to the beginning  
  ---

- Wait for the user to respond
- If they confirm the post looks good, proceed directly to Task 4 (no reprinting or extra prompts)

---

### Expected Outcome

- The user clearly sees their post
- The next-step options are unmistakably separate
- If approved, repurposing begins seamlessly




