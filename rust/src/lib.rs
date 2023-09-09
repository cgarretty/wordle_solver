use pyo3::prelude::*;
use rayon::prelude::*;

const GREEN: (bool, bool) = (true, true);
const YELLOW: (bool, bool) = (false, true);
const GRAY: (bool, bool) = (false, false);


#[pyfunction]
fn score_guess(answer: &str, guess: &str) -> [(bool, bool); 5] {
    let mut score = [GRAY; 5];
    let answer_chars = answer.as_bytes();
    let guess_chars = guess.as_bytes();
    let mut settled_letters = [false; 5];

    for i in 0..5 {
        if answer_chars[i] == guess_chars[i] {
            score[i] = GREEN;
            settled_letters[i] = true;
        } 
    }

    for i in 0..5 {
        if !settled_letters[i] { 
            if let Some(found_index) = answer_chars.iter().enumerate()
                .find(|(j, &c)| !settled_letters[*j] && c == guess_chars[i]) {
                    let (found_index, _) = found_index;
                    score[i] = YELLOW;
                    settled_letters[found_index] = true;
            } 
        }
    }

    return score
}

#[pyfunction]
fn score_all_words(answers: Vec<String>, guesses: Vec<String>) -> Vec<[(bool, bool); 5]> {
    let mut scores: Vec<[(bool, bool); 5]> = vec![];
    scores.reserve_exact(answers.len() * guesses.len());
    scores = guesses
        .par_iter() // Use parallel iterator
        .flat_map(|guess| {
            answers
                .iter()
                .map(|answer| score_guess(answer, guess))
                .collect::<Vec<[(bool, bool); 5]>>()
        }).collect::<Vec<[(bool, bool); 5]>>();

    scores
}

/// A Python module implemented in Rust.
#[pymodule]
fn rust(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(score_guess, m)?)?;
    m.add_function(wrap_pyfunction!(score_all_words, m)?)?;
    Ok(())
}