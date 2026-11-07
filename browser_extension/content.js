chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "scrape_blackboard") {
        try {
            // Extract Course Name & Code from page header or breadcrumbs
            let courseNameElement = document.querySelector('.course-name, h1.element-details, .path-bar span:last-child');
            let courseName = courseNameElement ? courseNameElement.innerText.trim() : "Unknown Course";
            
            let courseCodeMatch = courseName.match(/[A-Z]{3,4}\d{3,4}[A-Z]*/);
            let courseCode = courseCodeMatch ? courseCodeMatch[0] : "CMSC101";

            // Extract Grades if on a gradebook page
            let grades = [];
            let gradeRows = document.querySelectorAll('tr.grade-row, .gradebook-item, tr[id*="row"]');
            
            gradeRows.forEach(row => {
                let nameEl = row.querySelector('.item-title, .cell-title, td:first-child');
                let scoreEl = row.querySelector('.grade-value, .score, td:nth-child(2)');
                if (nameEl) {
                    grades.push({
                        assignment_name: nameEl.innerText.trim(),
                        score: scoreEl ? parseFloat(scoreEl.innerText) || null : null,
                        points_possible: 100.0,
                        weight: 10.0,
                        category: "Homework/Exam"
                    });
                }
            });

            // Extract Syllabus or Lecture text content from content areas
            let materials = [];
            let contentItems = document.querySelectorAll('.content_listItem, .item, article');
            
            contentItems.forEach(item => {
                let titleEl = item.querySelector('h3, h4, a.item-title');
                let textEl = item.querySelector('.details, .text, p');
                if (titleEl) {
                    materials.push({
                        title: titleEl.innerText.trim(),
                        material_type: "lecture",
                        text_content: textEl ? textEl.innerText.trim() : titleEl.innerText.trim()
                    });
                }
            });

            // Fallback sample data if page structure doesn't match standard items
            if (materials.length === 0) {
                materials.push({
                    title: "Syllabus & General Overview",
                    material_type: "syllabus",
                    text_content: document.body.innerText.substring(0, 3000) // Send page text context
                });
            }

            const payload = {
                course_code: courseCode,
                course_name: courseName,
                target_grade: "A",
                grades: grades,
                materials: materials
            };

            sendResponse({ status: "success", data: payload });
        } catch (error) {
            sendResponse({ status: "error", message: error.toString() });
        }
    }
    return true;
});