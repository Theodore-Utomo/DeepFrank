import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface MarkdownRendererProps {
  content: string;
  className?: string;
}

export function MarkdownRenderer({ content, className }: MarkdownRendererProps) {
  return (
    <div className={`prose prose-sm max-w-none dark:prose-invert ${className || ''}`}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          // Style code blocks
          code: ({ node, inline, className, children, ...props }) => {
            return inline ? (
              <code className="bg-muted px-1.5 py-0.5 rounded text-sm font-mono" {...props}>
                {children}
              </code>
            ) : (
              <code className="block bg-muted p-4 rounded-lg overflow-x-auto text-sm font-mono" {...props}>
                {children}
              </code>
            );
          },
          // Style pre blocks
          pre: ({ children, ...props }) => {
            return (
              <pre className="bg-muted p-4 rounded-lg overflow-x-auto my-2" {...props}>
                {children}
              </pre>
            );
          },
          // Style paragraphs
          p: ({ children, ...props }) => {
            return <p className="mb-2 last:mb-0" {...props}>{children}</p>;
          },
          // Style headings
          h1: ({ children, ...props }) => {
            return <h1 className="text-2xl font-bold mt-4 mb-2" {...props}>{children}</h1>;
          },
          h2: ({ children, ...props }) => {
            return <h2 className="text-xl font-bold mt-3 mb-2" {...props}>{children}</h2>;
          },
          h3: ({ children, ...props }) => {
            return <h3 className="text-lg font-semibold mt-2 mb-1" {...props}>{children}</h3>;
          },
          // Style lists
          ul: ({ children, ...props }) => {
            return <ul className="list-disc list-inside mb-2 space-y-1" {...props}>{children}</ul>;
          },
          ol: ({ children, ...props }) => {
            return <ol className="list-decimal list-inside mb-2 space-y-1" {...props}>{children}</ol>;
          },
          li: ({ children, ...props }) => {
            return <li className="ml-4" {...props}>{children}</li>;
          },
          // Style links
          a: ({ children, ...props }) => {
            return (
              <a className="text-primary underline hover:text-primary/80" {...props}>
                {children}
              </a>
            );
          },
          // Style blockquotes
          blockquote: ({ children, ...props }) => {
            return (
              <blockquote className="border-l-4 border-muted-foreground pl-4 italic my-2" {...props}>
                {children}
              </blockquote>
            );
          },
          // Style horizontal rules
          hr: ({ ...props }) => {
            return <hr className="my-4 border-t border-border" {...props} />;
          },
          // Style tables
          table: ({ children, ...props }) => {
            return (
              <div className="overflow-x-auto my-2">
                <table className="min-w-full border-collapse border border-border" {...props}>
                  {children}
                </table>
              </div>
            );
          },
          th: ({ children, ...props }) => {
            return (
              <th className="border border-border px-4 py-2 bg-muted font-semibold text-left" {...props}>
                {children}
              </th>
            );
          },
          td: ({ children, ...props }) => {
            return (
              <td className="border border-border px-4 py-2" {...props}>
                {children}
              </td>
            );
          },
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}

