<template>
  <div class="phish-attachment">
    <div class="phish-attachment__header">
      <span class="phish-attachment__name">{{ fileName }}</span>
      <q-btn
        v-if="attachmentUrl"
        flat
        label="Open"
        class="phish-attachment__link"
        @click="showDialog = true"
      />
    </div>

    <iframe
      v-if="canRenderInline"
      :title="fileName"
      class="phish-attachment__frame"
      sandbox=""
      referrerpolicy="no-referrer"
      loading="lazy"
      :srcdoc="iframeSrcdoc"
    ></iframe>

    <div v-else-if="attachmentUrl" class="phish-attachment__fallback">
      {{ fileName }}
    </div>

    <div v-else class="phish-attachment__fallback">
      No attachment available.
    </div>

    <!-- Attachment open confirmation dialog -->
     <q-dialog v-model="showDialog">
       <q-card>
         <q-card-section>
           Are you sure you want to open this attachment?
         </q-card-section>
         <q-card-actions align="right">
           <q-btn flat label="Cancel" v-close-popup />
           <q-btn flat label="Open" @click="openAttachment" />
         </q-card-actions>
       </q-card>
     </q-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'

interface PhishAttachmentLike {
  pk?: number | string
  report?: string | number
  filename?: string
  attachment?: string
}

const showDialog = ref(false)

const props = defineProps<{
  attachment: PhishAttachmentLike | null
}>()

const attachmentUrl = computed(() => props.attachment?.attachment || '')
const fileName = computed(() => props.attachment?.filename || 'Attachment')

const textContent = ref('')
const textError = ref(false)

function escapeHtml(value: string): string {
  return value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
}

function isImageFile(name: string): boolean {
  return /\.(png|jpe?g|gif|webp|bmp|svg|ico)$/i.test(name)
}

function isTextFile(name: string): boolean {
  return /\.(txt|csv|log|md|json|js|ts|html|htm|xml|yaml|yml|ini|conf|rtf)$/i.test(name)
}

const canRenderInline = computed(() => {
  const name = fileName.value || ''
  return !!attachmentUrl.value && (isImageFile(name) || isTextFile(name))
})

async function loadTextPreview() {
  if (!attachmentUrl.value || !isTextFile(fileName.value || '')) {
    textContent.value = ''
    return
  }

  try {
    const response = await fetch(attachmentUrl.value, {
      credentials: 'same-origin',
      cache: 'no-store'
    })

    if (!response.ok) {
      throw new Error(`Unable to load attachment (${response.status})`)
    }

    textContent.value = await response.text()
    textError.value = false
  } catch {
    textContent.value = 'Unable to load attachment preview.'
    textError.value = true
  }
}

function openAttachment() {
  if (attachmentUrl.value) {
    window.open(attachmentUrl.value, '_blank', 'noopener,noreferrer')
    showDialog.value = false
  }
}

onMounted(() => {
  loadTextPreview()
})

watch(
  () => [props.attachment?.attachment, props.attachment?.filename],
  () => {
    loadTextPreview()
  }
)

const iframeSrcdoc = computed(() => {
  const safeName = escapeHtml(fileName.value)
  const safeAttachmentUrl = escapeHtml(attachmentUrl.value)

  if (isImageFile(fileName.value || '')) {
    return `<!doctype html>
      <html lang="en">
        <head>
          <meta charset="utf-8" />
          <meta name="viewport" content="width=device-width, initial-scale=1" />
          <style>
            html, body {
              margin: 0;
              padding: 0;
              height: 100%;
              background: #f3f4f6;
              font-family: sans-serif;
            }
            body {
              display: flex;
              align-items: center;
              justify-content: center;
            }
            img {
              max-width: 100%;
              max-height: 70vh;
              display: block;
              border: 1px solid #e5e7eb;
              background: white;
              box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
            }
            noscript {
              color: #4b5563;
              font-size: 14px;
            }
          </style>
        </head>
        <body>
          <img src="${safeAttachmentUrl}" alt="${safeName}" />
        </body>
      </html>`
  }

  const content = textError.value
    ? 'Unable to load attachment preview.'
    : (textContent.value || 'Loading attachment…')

  const safeContent = escapeHtml(content)

  return `<!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <style>
          html, body {
            margin: 0;
            padding: 12px;
            background: white;
            color: #111827;
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
            font-size: 13px;
            line-height: 1.5;
          }
          pre {
            margin: 0;
            white-space: pre-wrap;
            word-break: break-word;
          }
          noscript {
            display: block;
            margin-top: 12px;
            color: #6b7280;
          }
        </style>
      </head>
      <body>
        <pre>${safeContent}</pre>
      </body>
    </html>`
})
</script>

<style scoped>
.phish-attachment {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: #fff;
  overflow: hidden;
}

.phish-attachment__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 12px;
  border-bottom: 1px solid #e5e7eb;
  background: #f9fafb;
}

.phish-attachment__name {
  font-weight: 600;
  color: #111827;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.phish-attachment__link,
.phish-attachment__fallback a {
  color: #2563eb;
  text-decoration: none;
}

.phish-attachment__link:hover,
.phish-attachment__fallback a:hover {
  text-decoration: underline;
}

.phish-attachment__frame {
  display: block;
  width: 100%;
  min-height: 280px;
  max-height: 70vh;
  border: 0;
  background: #f9fafb;
}

.phish-attachment__fallback {
  padding: 14px 12px;
  color: #374151;
}
</style>
