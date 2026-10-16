# Chat & Messaging (not currently used in this dashboard)

This dashboard has no chat/conversation feature today — this file exists
so that if one gets added (an AI assistant panel, a comments thread),
whoever builds it doesn't hand-roll what shadcn already solved.

Install: `npx shadcn@latest add message-scroller message bubble attachment marker`

## The core rule

A scrolling conversation that follows new messages, restores scroll
position, or jumps to the latest message uses `MessageScroller` — never
a hand-rolled `overflow-y-auto` div with manual `onScroll`/`useEffect`
stick-to-bottom logic. Streaming follow, anchoring, and a
jump-to-latest button are built into the component; a custom
`useStickToBottom` hook is very likely reimplementing something already
solved, worse.

```tsx
<MessageScrollerProvider autoScroll>
  <MessageScroller>
    <MessageScrollerViewport>
      <MessageScrollerContent>
        {messages.map((message) => (
          <MessageScrollerItem key={message.id} messageId={message.id}>
            <Message align={message.role === "user" ? "end" : "start"}>
              <Bubble>{message.content}</Bubble>
            </Message>
          </MessageScrollerItem>
        ))}
      </MessageScrollerContent>
      <MessageScrollerButton />
    </MessageScrollerViewport>
  </MessageScroller>
</MessageScrollerProvider>
```

Attachments use `Attachment` (not `Item` cards); system notes/dividers
use `Marker` (not `Separator` + a label).

Before building anything chat-shaped, read the full upstream reference
at `reference/shadcn-ui/ui/skills/shadcn/rules/chat.md` — it has the
complete nesting order, streaming patterns, and the escape-hatch hooks
for cases the components don't cover.
