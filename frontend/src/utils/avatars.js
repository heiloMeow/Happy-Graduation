export const colors = ['colorful', 'brown', 'white', 'white2', 'yellow'];

export const statuses = {
  normal: 'normal',
  smile: 'smile',
  okay: 'okay',
  annoying: 'annoying'
};

export const colorLabels = {
  colorful: 'Colorful',
  brown: 'Brown',
  white: 'White',
  white2: 'White 2',
  yellow: 'Yellow'
};

export function getAvatarUrl(color, status) {
  return `/avatars/${color}-${status}.png`;
}

export function getDefaultAvatar() {
  return getAvatarUrl('colorful', 'smile');
}

