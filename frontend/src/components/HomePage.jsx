import { useState, useMemo } from 'react';
import '../styles/HomePage.css';
import backgroundImage from '../mathematics-numbers-and-mathematical-data-ftjn425sx2rnifuk.jpg';
import ParticleBackground from './ParticleBackground';

function HomePage({ onEnter }) {
  const [isAnimating, setIsAnimating] = useState(false);

  const handleEnter = () => {
    setIsAnimating(true);
    setTimeout(() => {
      onEnter();
    }, 600);
  };

  // Generate floating math symbols
  const mathSymbols = useMemo(() => {
    const symbols = ['∫', 'π', '∑', '√', '∞', 'α', 'β', 'θ', 'Δ', '∂', '≈', '≠', '≤', '≥', '∈', '∀', '∃'];
    return Array.from({ length: 15 }, (_, i) => ({
      id: i,
      symbol: symbols[Math.floor(Math.random() * symbols.length)],
      left: Math.random() * 100,
      top: Math.random() * 100,
      duration: Math.random() * 10 + 15,
      delay: Math.random() * 5,
      size: Math.random() * 1.5 + 0.8
    }));
  }, []);

  return (
    <div className={`home-page ${isAnimating ? 'fade-out' : ''}`} style={{ backgroundImage: `url(${backgroundImage})` }}>
      <ParticleBackground />
      <div className="home-overlay"></div>
      
      {/* Floating Math Symbols */}
      <div className="math-symbols-container">
        {mathSymbols.map((item) => (
          <div
            key={item.id}
            className="floating-math-symbol"
            style={{
              left: `${item.left}%`,
              top: `${item.top}%`,
              animationDuration: `${item.duration}s`,
              animationDelay: `${item.delay}s`,
              fontSize: `${item.size}rem`
            }}
          >
            {item.symbol}
          </div>
        ))}
      </div>
      
      <div className="home-content">
        <div className="home-professional-badge">
          <div className="badge-icon">🎓</div>
        </div>
        
        <div className="home-icon-container">
          <div className="home-icon">∫</div>
          <div className="home-icon-accent">π</div>
          <div className="home-icon-accent">√</div>
          <div className="home-icon-accent">∑</div>
        </div>
        <h1 className="home-title">Math Routing Agent</h1>
        <p className="home-subtitle">AI-Powered Mathematical Problem Solver</p>
        <p className="home-description">
          Intelligent math problem routing system that automatically selects the best solving method 
          from Knowledge Base, Web Search, AI Generation, or Expert Review
        </p>
        
        <button className="enter-button" onClick={handleEnter}>
          <span>Start Solving</span>
          <span className="arrow">→</span>
        </button>
        
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">📚</div>
            <h3>Knowledge Base Search</h3>
            <p>Access pre-verified solutions from our comprehensive mathematical knowledge repository</p>
          </div>
          
          <div className="feature-card">
            <div className="feature-icon">🌐</div>
            <h3>Intelligent Web Search</h3>
            <p>Retrieve real-time solutions from authoritative mathematical resources across the web</p>
          </div>
          
          <div className="feature-card">
            <div className="feature-icon">🤖</div>
            <h3>AI-Powered Solutions</h3>
            <p>Generate detailed step-by-step explanations using advanced language models</p>
          </div>
          
          <div className="feature-card">
            <div className="feature-icon">👨‍🏫</div>
            <h3>Expert Verification</h3>
            <p>Leverage human expertise and feedback for complex mathematical challenges</p>
          </div>
        </div>

        {/* How It Works Section */}
        <div className="how-it-works">
          <h2 className="section-title">🔢 How It Works</h2>
          <div className="steps-container">
            <div className="step">
              <div className="step-number">1</div>
              <div className="step-icon">✏️</div>
              <h3>Enter Your Problem</h3>
              <p>Type or paste any math question</p>
            </div>
            <div className="step-arrow">→</div>
            <div className="step">
              <div className="step-number">2</div>
              <div className="step-icon">🎯</div>
              <h3>Smart Routing</h3>
              <p>System chooses best solving method</p>
            </div>
            <div className="step-arrow">→</div>
            <div className="step">
              <div className="step-number">3</div>
              <div className="step-icon">📝</div>
              <h3>Get Solution</h3>
              <p>Step-by-step detailed explanation</p>
            </div>
          </div>
        </div>

        {/* Key Features Section */}
        <div className="key-features">
          <h2 className="section-title">🌟 Key Features</h2>
          <div className="features-list">
            <div className="feature-item">
              <span className="check">✔</span>
              <span>Intelligent routing algorithm</span>
            </div>
            <div className="feature-item">
              <span className="check">✔</span>
              <span>Step-by-step explanations</span>
            </div>
            <div className="feature-item">
              <span className="check">✔</span>
              <span>LaTeX math rendering</span>
            </div>
            <div className="feature-item">
              <span className="check">✔</span>
              <span>Real-time web search</span>
            </div>
            <div className="feature-item">
              <span className="check">✔</span>
              <span>Human feedback loop</span>
            </div>
            <div className="feature-item">
              <span className="check">✔</span>
              <span>Supports JEE-level problems</span>
            </div>
          </div>
        </div>

        <button className="enter-button enter-bottom" onClick={handleEnter}>
          <span>Start Solving</span>
          <span className="arrow">→</span>
        </button>

        <div className="home-footer">
          <p className="footer-topics">Supporting Advanced Mathematics: Algebra • Calculus • Geometry • Statistics • Differential Equations • Linear Algebra</p>
          <div className="footer-tech">
            <p>© 2025 Math Routing Agent. All rights reserved.</p>
            <p>Powered by Advanced AI • Vector Database • Real-time Search • Graph-based Orchestration</p>
          </div>
        </div>
      </div>

      <div className="home-particles">
        {[...Array(20)].map((_, i) => (
          <div
            key={i}
            className="home-particle"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 5}s`,
              animationDuration: `${5 + Math.random() * 5}s`
            }}
          />
        ))}
        
        {/* Grid Pattern */}
        <div className="grid-pattern"></div>
        
        {/* Mathematical symbols scattered throughout */}
        <div className="math-symbol" style={{ top: '10%', left: '5%', fontSize: '2.5rem' }}>π</div>
        <div className="math-symbol" style={{ top: '15%', right: '8%', fontSize: '2rem' }}>√</div>
        <div className="math-symbol" style={{ bottom: '20%', left: '10%', fontSize: '3rem' }}>∑</div>
        <div className="math-symbol" style={{ top: '70%', right: '12%', fontSize: '2.2rem' }}>∫</div>
        <div className="math-symbol" style={{ top: '35%', left: '3%', fontSize: '2rem' }}>π</div>
        <div className="math-symbol" style={{ bottom: '30%', right: '5%', fontSize: '2.5rem' }}>√</div>
        <div className="math-symbol" style={{ top: '55%', left: '8%', fontSize: '2.8rem' }}>∑</div>
        <div className="math-symbol" style={{ top: '25%', right: '15%', fontSize: '2rem' }}>∫</div>
        <div className="math-symbol" style={{ bottom: '40%', left: '15%', fontSize: '2.3rem' }}>π</div>
        <div className="math-symbol" style={{ top: '80%', right: '20%', fontSize: '2rem' }}>√</div>
        <div className="math-symbol" style={{ top: '45%', left: '12%', fontSize: '2.4rem' }}>∑</div>
        <div className="math-symbol" style={{ bottom: '15%', right: '25%', fontSize: '2.6rem' }}>∫</div>
        <div className="math-symbol" style={{ top: '60%', right: '30%', fontSize: '2rem' }}>π</div>
        <div className="math-symbol" style={{ bottom: '50%', left: '20%', fontSize: '2.2rem' }}>√</div>
        <div className="math-symbol" style={{ top: '30%', left: '25%', fontSize: '2.5rem' }}>∑</div>
        <div className="math-symbol" style={{ bottom: '25%', right: '35%', fontSize: '2.3rem' }}>∫</div>
        <div className="math-symbol" style={{ top: '50%', right: '40%', fontSize: '2rem' }}>π</div>
        <div className="math-symbol" style={{ bottom: '60%', left: '30%', fontSize: '2.4rem' }}>√</div>
        <div className="math-symbol" style={{ top: '40%', right: '45%', fontSize: '2.6rem' }}>∑</div>
        <div className="math-symbol" style={{ bottom: '35%', left: '35%', fontSize: '2.2rem' }}>∫</div>
        
        {/* Geometric Shapes */}
        <div className="geometric-shape circle" style={{ 
          top: '15%', 
          left: '85%',
          width: '150px',
          height: '150px'
        }}></div>
        
        <div className="geometric-shape triangle" style={{ 
          bottom: '20%', 
          left: '10%'
        }}></div>
        
        <div className="geometric-shape square" style={{ 
          top: '70%', 
          right: '15%',
          width: '100px',
          height: '100px'
        }}></div>
        
        <div className="geometric-shape hexagon" style={{ 
          top: '25%', 
          left: '8%'
        }}></div>
        
        {/* Mathematical formula decorations */}
        <div className="math-decoration" style={{ 
          position: 'absolute', 
          top: '5%', 
          right: '10%',
          fontSize: '3rem',
          color: 'rgba(255, 255, 255, 0.04)',
          animation: 'floatSlow 18s ease-in-out infinite',
          userSelect: 'none'
        }}>
          ∫ f(x)dx
        </div>
        
        <div className="math-decoration" style={{ 
          position: 'absolute', 
          bottom: '10%', 
          left: '5%',
          fontSize: '2.5rem',
          color: 'rgba(255, 255, 255, 0.04)',
          animation: 'floatSlow 22s ease-in-out infinite reverse',
          userSelect: 'none'
        }}>
          e^(iπ) + 1 = 0
        </div>
        
        <div className="math-decoration" style={{ 
          position: 'absolute', 
          top: '40%', 
          left: '2%',
          fontSize: '2rem',
          color: 'rgba(255, 255, 255, 0.03)',
          animation: 'floatSlow 20s ease-in-out infinite',
          userSelect: 'none'
        }}>
          √x² + y²
        </div>
        
        <div className="math-decoration" style={{ 
          position: 'absolute', 
          top: '60%', 
          right: '5%',
          fontSize: '2.5rem',
          color: 'rgba(255, 255, 255, 0.04)',
          animation: 'floatSlow 24s ease-in-out infinite reverse',
          userSelect: 'none'
        }}>
          ∂f/∂x
        </div>
        
        <div className="math-decoration" style={{ 
          position: 'absolute', 
          top: '80%', 
          left: '50%',
          fontSize: '2rem',
          color: 'rgba(255, 255, 255, 0.03)',
          animation: 'floatSlow 19s ease-in-out infinite',
          userSelect: 'none'
        }}>
          lim(x→∞)
        </div>
        
        <div className="math-decoration" style={{ 
          position: 'absolute', 
          top: '12%', 
          left: '30%',
          fontSize: '1.8rem',
          color: 'rgba(255, 255, 255, 0.03)',
          animation: 'floatSlow 21s ease-in-out infinite reverse',
          userSelect: 'none'
        }}>
          Σ(n=1 to ∞)
        </div>
        
        <div className="math-decoration" style={{ 
          position: 'absolute', 
          top: '35%', 
          right: '8%',
          fontSize: '2.2rem',
          color: 'rgba(255, 255, 255, 0.04)',
          animation: 'floatSlow 17s ease-in-out infinite',
          userSelect: 'none'
        }}>
          ∇ × F
        </div>
        
        <div className="math-decoration" style={{ 
          position: 'absolute', 
          bottom: '25%', 
          right: '25%',
          fontSize: '1.9rem',
          color: 'rgba(255, 255, 255, 0.03)',
          animation: 'floatSlow 23s ease-in-out infinite reverse',
          userSelect: 'none'
        }}>
          ∂²f/∂x²
        </div>
        
        <div className="math-decoration" style={{ 
          position: 'absolute', 
          top: '55%', 
          left: '12%',
          fontSize: '2.1rem',
          color: 'rgba(255, 255, 255, 0.04)',
          animation: 'floatSlow 16s ease-in-out infinite',
          userSelect: 'none'
        }}>
          ∮ E·dl
        </div>
        
        <div className="math-decoration" style={{ 
          position: 'absolute', 
          top: '25%', 
          right: '20%',
          fontSize: '1.7rem',
          color: 'rgba(255, 255, 255, 0.03)',
          animation: 'floatSlow 26s ease-in-out infinite reverse',
          userSelect: 'none'
        }}>
          ∏(i=1 to n)
        </div>
        
        <div className="math-decoration" style={{ 
          position: 'absolute', 
          bottom: '15%', 
          left: '35%',
          fontSize: '2rem',
          color: 'rgba(255, 255, 255, 0.04)',
          animation: 'floatSlow 19s ease-in-out infinite',
          userSelect: 'none'
        }}>
          ∞
        </div>
        
        <div className="math-decoration" style={{ 
          position: 'absolute', 
          top: '45%', 
          right: '35%',
          fontSize: '1.8rem',
          color: 'rgba(255, 255, 255, 0.03)',
          animation: 'floatSlow 21s ease-in-out infinite reverse',
          userSelect: 'none'
        }}>
          λ ≈ h/p
        </div>
        
        <div className="math-decoration" style={{ 
          position: 'absolute', 
          top: '8%', 
          left: '15%',
          fontSize: '2rem',
          color: 'rgba(255, 255, 255, 0.04)',
          animation: 'floatSlow 18s ease-in-out infinite',
          userSelect: 'none'
        }}>
          Φ
        </div>
        
        <div className="math-decoration" style={{ 
          position: 'absolute', 
          bottom: '35%', 
          right: '10%',
          fontSize: '1.9rem',
          color: 'rgba(255, 255, 255, 0.03)',
          animation: 'floatSlow 24s ease-in-out infinite reverse',
          userSelect: 'none'
        }}>
          ∀x∃y
        </div>
      </div>
    </div>
  );
}

export default HomePage;
