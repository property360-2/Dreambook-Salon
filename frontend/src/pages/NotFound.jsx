import { Link } from 'react-router-dom';

export function NotFound() {
  return (
    <div className="screen-centered">
      <div className="card" style={{ textAlign: 'center' }}>
        <h2 style={{ marginTop: 0 }}>Nothing to see here</h2>
        <p className="muted">
          The page you are looking for was moved or never existed.
        </p>
        <Link to="/" className="button">
          Back to dashboard
        </Link>
      </div>
    </div>
  );
}
