import { useState } from 'react';
import '../styles/FeedbackContainer.css';

function FeedbackContainer({
  onFeedbackSubmit,
  onSkip,
  submitted,
  isLoading
}) {
  const [rating, setRating] = useState(0);
  const [hoveredRating, setHoveredRating] = useState(0);
  const [feedback, setFeedback] = useState('');
  const [showDetailed, setShowDetailed] = useState(false);

  const handleQuickFeedback = (type) => {
    onFeedbackSubmit(type, '');
  };

  const handleDetailedFeedback = () => {
    const detailedText = `Rating: ${rating}/5\n${feedback}`;
    onFeedbackSubmit('detailed', detailedText);
  };

  const handleStarClick = (starRating) => {
    setRating(starRating);
    setShowDetailed(true);
  };

  if (submitted) {
    return (
      <div className="feedback-container fade-in">
        <div className="feedback-success">
          ✅ Thank you for your feedback! This helps us improve.
        </div>
      </div>
    );
  }

  return (
    <div className="feedback-container fade-in" role="region" aria-label="Feedback section">
      <h3 className="feedback-title">
        🔄 Was this solution helpful?
      </h3>

      <div className="star-rating-section">
        <div className="star-rating">
          {[1, 2, 3, 4, 5].map((star) => (
            <button
              key={star}
              className={`star ${star <= (hoveredRating || rating) ? 'filled' : ''}`}
              onClick={() => handleStarClick(star)}
              onMouseEnter={() => setHoveredRating(star)}
              onMouseLeave={() => setHoveredRating(0)}
              aria-label={`Rate ${star} stars`}
              disabled={isLoading}
            >
              ⭐
            </button>
          ))}
        </div>
        {rating > 0 && (
          <div className="rating-text">
            {rating === 5 ? 'Excellent!' : rating === 4 ? 'Very Good!' : rating === 3 ? 'Good' : rating === 2 ? 'Fair' : 'Needs Improvement'}
          </div>
        )}
      </div>

      <div className="quick-feedback-buttons">
        <button
          onClick={() => handleQuickFeedback('helpful')}
          className="feedback-thumb-button thumb-up"
          title="This solution was helpful"
          disabled={isLoading}
          aria-label="Mark as helpful"
        >
          👍 Helpful
        </button>
        <button
          onClick={() => handleQuickFeedback('👎')}
          className="feedback-thumb-button thumb-down"
          title="This solution needs improvement"
          disabled={isLoading}
          aria-label="Mark as needs fixing"
        >
          👎 Needs Fix
        </button>
      </div>

      {(showDetailed || rating > 0) && (
        <div className="detailed-feedback-section fade-in">
          <div className="mb-15">
            <label className="feedback-label" htmlFor="feedback">
              💬 Add your comment (optional):
            </label>
            <textarea
              id="feedback"
              value={feedback}
              onChange={e => setFeedback(e.target.value)}
              placeholder="Tell us how we can improve this solution..."
              className="feedback-textarea"
              disabled={isLoading}
              rows="4"
            />
          </div>

          <div className="feedback-buttons">
            <button
              onClick={handleDetailedFeedback}
              className="feedback-button feedback-submit"
              disabled={isLoading || rating === 0}
            >
              {isLoading ? '⏳ Submitting...' : 'Submit Feedback'}
            </button>
          </div>
        </div>
      )}

      <button
        onClick={onSkip}
        className="feedback-skip-button"
        disabled={isLoading}
        aria-label="Skip feedback"
      >
        Skip Feedback
      </button>
    </div>
  );
}

export default FeedbackContainer;
