use numpy::{PyArray3};
use pyo3::prelude::*;
use pyo3::types::{IntoPyDict, PyDict};


#[pyfunction]
fn score_guess(answer: &str, guess: &str) -> Vec<Vec<bool>> {
    let mut score = vec![vec![false, false]; 5];
    let answer_chars = answer.as_bytes();
    let guess_chars = guess.as_bytes();
    let mut settled_letters = [false; 5];

    for i in 0..5 {
        if answer_chars[i] == guess_chars[i] {
            score[i] = vec![true, true];
            settled_letters[i] = true;
        } 
    }

    for i in 0..5 {
        if !settled_letters[i] { 
            if let Some(found_index) = answer_chars.iter().enumerate()
                .find(|(j, &c)| !settled_letters[*j] && c == guess_chars[i]) {
                    let (found_index, _) = found_index;
                    score[i] = vec![false, true];
                    settled_letters[found_index] = true;
            } 
        }
    }

    return score
}

#[pyfunction]
fn score_all_words(py: Python, answers: Vec<String>, guesses: Vec<String>) -> PyResult<Py<PyDict>> {
    let mut score_card = vec![];
    score_card.reserve_exact(guesses.len());
    
    for guess in guesses {
        let mut scores = vec![];
        scores.reserve_exact(answers.len());
        for answer in &answers {
            scores.push(score_guess(answer, &guess));
        };
        let numpy_array = PyArray3::from_vec3(py, &scores);
        score_card.push((guess, numpy_array?.to_object(py)));
    }

    let locals = score_card.into_py_dict(py);

    Ok(locals.into())
}

/// A Python module implemented in Rust.
#[pymodule]
fn rust(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(score_guess, m)?)?;
    m.add_function(wrap_pyfunction!(score_all_words, m)?)?;
    Ok(())
}

