# Integration Guide for ZeroDoc

## Quick Start

Generate complete documentation with one command:

```bash
# Install zerodoc-gen
pip install zerodoc-gen

# Generate docs in ./docs folder
autodoc generate .

# Or serve immediately
autodoc generate . --serve
```

## Integration with Different Frameworks

### Next.js / React

1. Generate docs in the `public` folder:
```bash
autodoc generate . --output public/docs
```

2. Access at: `http://localhost:3000/docs`

### Express / Node.js

1. Generate docs:
```bash
autodoc generate . --output docs
```

2. Serve static files:
```javascript
app.use('/docs', express.static('docs'));
```

### Python Flask

1. Generate docs:
```bash
autodoc generate . --output static/docs
```

2. Access at: `http://localhost:5000/static/docs`

### GitHub Pages

1. Generate in `docs` folder:
```bash
autodoc generate . --output docs
```

2. Enable GitHub Pages in Settings → Pages → Source: `/docs`

### Netlify / Vercel

Add to build command:
```bash
pip install zerodoc-gen && autodoc generate . --output docs
```

## Customization

### Custom Output Location
```bash
autodoc generate . --output my-docs
```

### Custom Port for Serving
```bash
autodoc generate . --serve --port 8080
```

### CI/CD Integration

#### GitHub Actions
```yaml
- name: Generate Docs
  run: |
    pip install zerodoc-gen
    autodoc generate .
```

#### GitLab CI
```yaml
generate-docs:
  script:
    - pip install zerodoc-gen
    - autodoc generate .
  artifacts:
    paths:
      - docs/
```

## API Routes

For frameworks with routing, you can create a route to serve the docs:

### Next.js API Route
Create `pages/api/docs/[...path].js`:
```javascript
import fs from 'fs';
import path from 'path';

export default function handler(req, res) {
  const { path: docPath } = req.query;
  const filePath = path.join(process.cwd(), 'docs', ...docPath);
  
  if (fs.existsSync(filePath)) {
    const content = fs.readFileSync(filePath);
    res.setHeader('Content-Type', 'text/html');
    res.send(content);
  } else {
    res.status(404).send('Not found');
  }
}
```

## Docker Integration

Add to Dockerfile:
```dockerfile
RUN pip install zerodoc-gen
RUN autodoc generate . --output /app/docs
```

## Common Patterns

### Auto-generate on commit
`.git/hooks/pre-commit`:
```bash
#!/bin/sh
autodoc generate . --output docs
git add docs/
```

### Include in package.json
```json
{
  "scripts": {
    "docs": "npx zerodoc-gen generate .",
    "docs:serve": "npx zerodoc-gen generate . --serve"
  }
}
```

## Troubleshooting

### Command not found
Use the full path or module syntax:
```bash
python3 -m autodoc.cli generate .
```

### Permission errors
Install with user flag:
```bash
pip install --user zerodoc-gen
```

### Path issues
Add to PATH:
```bash
export PATH="$HOME/.local/bin:$PATH"
```