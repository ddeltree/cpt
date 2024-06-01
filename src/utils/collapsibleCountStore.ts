let count = 0;

export function getCountId() {
  const id = "collapsible-" + count.toString();
  incrementCount();
  return id;
}

function incrementCount() {
  count += 1;
}
