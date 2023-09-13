use pyo3::prelude::*;
use numpy::{PyArray3};

const GREEN: u8 = 2;
const YELLOW: u8 = 1;
const GRAY: u8 = 0;

#[pyfunction]
fn score_guess(answer: &str, guess: &str) -> [u8; 5] {
    let mut score: [u8; 5] = [GRAY; 5];
    let mut settled_answer_letters = [false; 5];

    for (i, (a, g)) in guess.chars().zip(answer.chars()).enumerate() {
        if a == g {
            score[i] = GREEN;
            settled_answer_letters[i] = true;
        }
    }

    for (i, letter) in guess.chars().enumerate() {
        if let Some(found_index) = answer.chars().zip(settled_answer_letters).position(|c| c.0 == letter && !c.1) {
            if score[i] != GREEN {
                score[i] = YELLOW;
                settled_answer_letters[found_index] = true ;
            }
        }
    }
    return score
}

#[pyfunction]
fn score_all_words(py: Python, answers: Vec<&str>, guesses: Vec<&str>) -> Py<PyAny> {    
    let mut score_card = vec![];
    let mut scores = vec![];
    score_card.reserve_exact(guesses.len());
    scores.reserve_exact(answers.len());

    for guess in guesses.iter() {
        scores.clear();
        scores = answers.iter().map(|answer| score_guess(&answer, &guess).to_vec()).collect();
        score_card.push(scores.clone());
    }

    return PyArray3::from_vec3(py, &score_card).expect("REASON").to_object(py).into();
}


/// A Python module implemented in Rust.
#[pymodule]
fn rust(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(score_guess, m)?)?;
    m.add_function(wrap_pyfunction!(score_all_words, m)?)?;
    Ok(())
}

