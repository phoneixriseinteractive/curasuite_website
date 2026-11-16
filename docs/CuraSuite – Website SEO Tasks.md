CuraSuite – Website SEO Tasks
Developer task list for curasuite.app
1. Tasks
Add a sitemap. No sitemap was found. Please add one at: https://curasuite.app/sitemap.xml
Add canonical tags. The canonical tag is missing from pages. Please add it to all pages. Example page: https://curasuite.app/products/curacms/
Update the CuraCMS product page. Replace the current content and add real CMS screenshots/video, doctor website templates, appointment workflow, SEO editor, integrations, migration, security and case studies. Page: https://curasuite.app/products/curacms/
Reference screenshot for task 3


Add schema markup. Details and code are in Section 2 below.
2. Schema markup to add
Add each JSON-LD script to the <head> section of the pages listed. Replace every placeholder marked “ADD YOUR…” with real details before publishing.
2.1 Organization + LocalBusiness (all pages)
Reusable sitewide schema. Add to the <head> of all pages.
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Organization",
      "@id": "https://curasuite.app/#organization",
      "name": "CuraSuite",
      "legalName": "PhoenixRise Interactive Pvt. Ltd.",
      "url": "https://curasuite.app/",
      "email": "hello@curasuite.app",
      "telephone": "+91 88828 14698",
      "description": "CuraSuite is a healthcare technology platform providing digital solutions for doctors, clinics, and pathology laboratories in India.",
      "areaServed": {
        "@type": "Country",
        "name": "India"
      },
      "knowsAbout": [
        "Healthcare Management Platform",
        "Clinic Management Software",
        "Healthcare Technology",
        "Doctor Website Development",
        "Pathology Lab Management Software",
        "Healthcare Automation",
        "Digital Healthcare Solutions"
      ]
    },
    {
      "@type": "LocalBusiness",
      "@id": "https://curasuite.app/#localbusiness",
      "name": "CuraSuite",
      "url": "https://curasuite.app/",
      "image": "https://curasuite.app/",
      "telephone": "+91 88828 14698",
      "email": "hello@curasuite.app",
      "description": "Healthcare technology solutions for doctors, clinics, and pathology laboratories.",
      "parentOrganization": {
        "@id": "https://curasuite.app/#organization"
      },
      "address": {
        "@type": "PostalAddress",
        "streetAddress": "ADD YOUR OFFICE STREET ADDRESS",
        "addressLocality": "ADD YOUR CITY",
        "addressRegion": "ADD YOUR STATE",
        "postalCode": "ADD YOUR PIN CODE",
        "addressCountry": "IN"
      },
      "areaServed": {
        "@type": "Country",
        "name": "India"
      }
    }
  ]
}
</script>

2.2 Product schema (CuraCMS product page only)
Add only on https://curasuite.app/products/curacms/
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "SoftwareApplication",
      "@id": "https://curasuite.app/products/curacms/#software",
      "name": "CuraCMS",
      "url": "https://curasuite.app/products/curacms/",
      "applicationCategory": "BusinessApplication",
      "operatingSystem": "Web browser",
      "description": "CuraCMS is a healthcare-focused website management platform for doctors and clinics, offering appointment booking, patient CRM, blogging, SEO tools, analytics, AI chatbot, and WhatsApp integration.",
      "provider": {
        "@id": "https://curasuite.app/#organization"
      },
      "featureList": [
        "Healthcare Website CMS",
        "Drag-and-Drop Page Builder",
        "Online Appointment Booking",
        "Patient CRM",
        "Healthcare Blog Engine",
        "SEO Tools and Schema Markup",
        "Analytics Dashboard",
        "Gemini-Powered AI Chatbot",
        "WhatsApp Integration",
        "Landing Page Builder"
      ],
      "offers": [
        {
          "@type": "Offer",
          "name": "CuraCMS Starter",
          "price": "9999",
          "priceCurrency": "INR",
          "description": "Starter annual subscription",
          "url": "https://curasuite.app/products/curacms/"
        },
        {
          "@type": "Offer",
          "name": "CuraCMS Professional",
          "price": "19999",
          "priceCurrency": "INR",
          "description": "Professional annual subscription",
          "url": "https://curasuite.app/products/curacms/"
        }
      ]
    },
    {
      "@type": "WebPage",
      "@id": "https://curasuite.app/products/curacms/#webpage",
      "url": "https://curasuite.app/products/curacms/",
      "name": "CuraCMS – Professional Website Platform for Doctors",
      "description": "Build a professional doctor or clinic website with CuraCMS, featuring appointment booking, patient CRM, SEO tools, blogging, and AI chatbot.",
      "isPartOf": {
        "@id": "https://curasuite.app/#website"
      },
      "mainEntity": {
        "@id": "https://curasuite.app/products/curacms/#software"
      },
      "inLanguage": "en-IN"
    },
    {
      "@type": "BreadcrumbList",
      "@id": "https://curasuite.app/products/curacms/#breadcrumb",
      "itemListElement": [
        {
          "@type": "ListItem",
          "position": 1,
          "name": "Home",
          "item": "https://curasuite.app/"
        },
        {
          "@type": "ListItem",
          "position": 2,
          "name": "Products",
          "item": "https://curasuite.app/products/"
        },
        {
          "@type": "ListItem",
          "position": 3,
          "name": "CuraCMS",
          "item": "https://curasuite.app/products/curacms/"
        }
      ]
    }
  ]
}
</script>

2.3 Article schema (all blog posts)
Add to every blog post. The example below is for the “Best Clinic Management Software in India” article; update the URL, headline, description, date, author and keywords for each post.
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "BlogPosting",
      "@id": "https://curasuite.app/blog/best-clinic-management-software-in-india-features-to-compare-before-choosing/#article",
      "mainEntityOfPage": {
        "@type": "WebPage",
        "@id": "https://curasuite.app/blog/best-clinic-management-software-in-india-features-to-compare-before-choosing/"
      },
      "headline": "Best Clinic Management Software in India: Features to Compare Before Choosing",
      "description": "Choosing the right clinic management software in India can improve appointments, patient records, billing and daily clinic operations. Explore the essential features to compare before making your decision.",
      "datePublished": "2026-11-13",
      "author": {
        "@type": "Person",
        "name": "Safeera Safeeq"
      },
      "publisher": {
        "@id": "https://curasuite.app/#organization"
      },
      "articleSection": "Practice Management",
      "inLanguage": "en-IN",
      "keywords": [
        "Best Clinic Management Software in India",
        "Clinic Management Software",
        "Healthcare Management Software",
        "Clinic Automation Software",
        "Practice Management Software"
      ],
      "about": [
        {
          "@type": "Thing",
          "name": "Clinic Management Software"
        },
        {
          "@type": "Thing",
          "name": "Healthcare Technology"
        },
        {
          "@type": "Thing",
          "name": "Clinic Automation"
        }
      ]
    },
    {
      "@type": "BreadcrumbList",
      "@id": "https://curasuite.app/blog/best-clinic-management-software-in-india-features-to-compare-before-choosing/#breadcrumb",
      "itemListElement": [
        {
          "@type": "ListItem",
          "position": 1,
          "name": "Home",
          "item": "https://curasuite.app/"
        },
        {
          "@type": "ListItem",
          "position": 2,
          "name": "Blog",
          "item": "https://curasuite.app/blog/"
        },
        {
          "@type": "ListItem",
          "position": 3,
          "name": "Best Clinic Management Software in India: Features to Compare Before Choosing",
          "item": "https://curasuite.app/blog/best-clinic-management-software-in-india-features-to-compare-before-choosing/"
        }
      ]
    }
  ]
}
</script>


