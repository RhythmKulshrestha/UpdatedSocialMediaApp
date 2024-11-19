import streamlit as st
from helpers.FacebookMinimal import FacebookMinimal

def run(operation):
    
        # Initialize FacebookMinimal instance
    try:
        fb = FacebookMinimal()
        st.success(f"Initialized Facebook API with Page ID: {fb.page_id}")
    except Exception as e:
        st.error(f"Failed to initialize Facebook API: {e}")


        # Check if Facebook API was successfully initialized before proceeding
    if fb and fb.token:
        
        # --- CREATE POST ---
        if operation == "Create Post":
            st.header("Create a New Facebook Post")
            
            # Input for the post message
            message = st.text_area("Message", "")
            
            if st.button("Create Post"):
                try:
                    post = fb.create_post(message)
                    if post and 'id' in post:
                        post_id = post['id']
                        st.success(f"Post created successfully! Post ID: {post_id}")
                        
                        # Display a button to view the post on Facebook
                        post_url = f"https://www.facebook.com/{fb.page_id}/posts/{post_id.split('_')[-1]}"
                        st.markdown(f"[View Post on Facebook]({post_url})", unsafe_allow_html=True)
                    else:
                        st.error("Failed to create post. Please check your permissions.")
                except Exception as e:
                    st.error(f"Error creating post: {e}")
        
        # --- READ POST ---
        elif operation == "Read Post":
            st.header("Read a Facebook Post")
            
            # Input for the post ID
            post_id = st.text_input("Post ID", "")
            
            if st.button("Read Post"):
                try:
                    post_content = fb.read_post(post_id)
                    if post_content:
                        st.write("Post Content:")
                        st.json(post_content)
                        
                        # Display a button to view the post on Facebook
                        post_url = f"https://www.facebook.com/{fb.page_id}/posts/{post_id.split('_')[-1]}"
                        st.markdown(f"[View Post on Facebook]({post_url})", unsafe_allow_html=True)
                    else:
                        st.error("Failed to read post. Make sure the Post ID is correct.")
                except Exception as e:
                    st.error(f"Error reading post: {e}")
        
        # --- UPDATE POST ---
        elif operation == "Update Post":
            st.header("Update a Facebook Post")
            
            # Input for the post ID and new message
            post_id = st.text_input("Post ID to Update", "")
            new_message = st.text_area("New Message", "")
            
            if st.button("Update Post"):
                try:
                    updated_post = fb.update_post(post_id, new_message)
                    if updated_post:
                        st.success("Post updated successfully!")
                        
                        # Display a button to view the updated post on Facebook
                        post_url = f"https://www.facebook.com/{fb.page_id}/posts/{post_id.split('_')[-1]}"
                        st.markdown(f"[View Updated Post on Facebook]({post_url})", unsafe_allow_html=True)
                    else:
                        st.error("Failed to update post. Make sure you have the correct Post ID and permissions.")
                except Exception as e:
                    st.error(f"Error updating post: {e}")
        
        # --- DELETE POST ---
        elif operation == "Delete Post":
            st.header("Delete a Facebook Post")
            
            # Input for the post ID to delete
            post_id = st.text_input("Post ID to Delete", "")
            
            if st.button("Delete Post"):
                try:
                    delete_result = fb.delete_post(post_id)
                    if delete_result:
                        st.success("Post deleted successfully!")
                    else:
                        st.error("Failed to delete post. Make sure the Post ID is correct.")
                except Exception as e:
                    st.error(f"Error deleting post: {e}")

    else:
        st.warning("Facebook API not initialized. Check your credentials and .env file.")

