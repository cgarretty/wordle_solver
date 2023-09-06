use pyo3::prelude::*;
use rayon::prelude::*;

#[pyfunction]
fn score_guess(answer: &str, guess: &str) -> ([bool; 5], [bool; 5]) {
    let mut in_word: [bool; 5] = [false; 5];
    let mut in_position: [bool; 5] = [false; 5];
    let mut answer_chars: Vec<char> = answer.chars().collect();
    let guess_chars: Vec<char> = guess.chars().collect();


    for i in 0..5 {
        if answer_chars[i] == guess_chars[i] {
            in_word[i] = true;
            answer_chars[i] = ' ';
        } 
    }

    for i in 0..5 {
        if answer_chars.contains(&guess_chars[i]) && !in_word[i] {
            in_position[i] = true;
        }
    }

    return (in_word, in_position);
}

#[pyfunction]
fn score_all_words(answers: Vec<String>, guesses: Vec<String>) -> Vec<([bool; 5], [bool; 5])> {
    let mut scores: Vec<([bool; 5], [bool; 5])> = vec![];
    scores.reserve_exact(answers.len() * guesses.len());
    scores = guesses
        .par_iter() // Use parallel iterator
        .flat_map(|guess| {
            answers
                .iter()
                .map(|answer| score_guess(answer, guess))
                .collect::<Vec<_>>()
        })
        .collect();

    scores
}

/// A Python module implemented in Rust.
#[pymodule]
fn rust(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(score_guess, m)?)?;
    m.add_function(wrap_pyfunction!(score_all_words, m)?)?;
    Ok(())
}