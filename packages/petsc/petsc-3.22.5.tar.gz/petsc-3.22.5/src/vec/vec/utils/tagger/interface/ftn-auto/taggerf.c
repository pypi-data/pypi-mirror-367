#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* tagger.c */
/* Fortran interface file */

/*
* This file was generated automatically by bfort from the C source
* file.  
 */

#ifdef PETSC_USE_POINTER_CONVERSION
#if defined(__cplusplus)
extern "C" { 
#endif 
extern void *PetscToPointer(void*);
extern int PetscFromPointer(void *);
extern void PetscRmPointer(void*);
#if defined(__cplusplus)
} 
#endif 

#else

#define PetscToPointer(a) (a ? *(PetscFortranAddr *)(a) : 0)
#define PetscFromPointer(a) (PetscFortranAddr)(a)
#define PetscRmPointer(a)
#endif

#include "petscvec.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vectaggercreate_ VECTAGGERCREATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vectaggercreate_ vectaggercreate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vectaggersettype_ VECTAGGERSETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vectaggersettype_ vectaggersettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vectaggergettype_ VECTAGGERGETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vectaggergettype_ vectaggergettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vectaggerdestroy_ VECTAGGERDESTROY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vectaggerdestroy_ vectaggerdestroy
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vectaggersetup_ VECTAGGERSETUP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vectaggersetup_ vectaggersetup
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vectaggersetblocksize_ VECTAGGERSETBLOCKSIZE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vectaggersetblocksize_ vectaggersetblocksize
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vectaggergetblocksize_ VECTAGGERGETBLOCKSIZE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vectaggergetblocksize_ vectaggergetblocksize
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vectaggersetinvert_ VECTAGGERSETINVERT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vectaggersetinvert_ vectaggersetinvert
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vectaggergetinvert_ VECTAGGERGETINVERT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vectaggergetinvert_ vectaggergetinvert
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vectaggerview_ VECTAGGERVIEW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vectaggerview_ vectaggerview
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  vectaggercreate_(MPI_Fint * comm,VecTagger *tagger, int *ierr)
{
PETSC_FORTRAN_OBJECT_CREATE(tagger);
 PetscBool tagger_null = !*(void**) tagger ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(tagger);
*ierr = VecTaggerCreate(
	MPI_Comm_f2c(*(comm)),tagger);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! tagger_null && !*(void**) tagger) * (void **) tagger = (void *)-2;
}
PETSC_EXTERN void  vectaggersettype_(VecTagger tagger,char *type, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(tagger);
/* insert Fortran-to-C conversion for type */
  FIXCHAR(type,cl0,_cltmp0);
*ierr = VecTaggerSetType(
	(VecTagger)PetscToPointer((tagger) ),_cltmp0);
  FREECHAR(type,_cltmp0);
}
PETSC_EXTERN void  vectaggergettype_(VecTagger tagger,char *type, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(tagger);
*ierr = VecTaggerGetType(
	(VecTagger)PetscToPointer((tagger) ),(const char **)&_cltmp0);
/* insert C-to-Fortran conversion for type */
*ierr = PetscStrncpy(type, _cltmp0, cl0);
                        if (*ierr) return;
                        FIXRETURNCHAR(PETSC_TRUE, type, cl0);
}
PETSC_EXTERN void  vectaggerdestroy_(VecTagger *tagger, int *ierr)
{
PETSC_FORTRAN_OBJECT_F_DESTROYED_TO_C_NULL(tagger);
 PetscBool tagger_null = !*(void**) tagger ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(tagger);
*ierr = VecTaggerDestroy(tagger);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! tagger_null && !*(void**) tagger) * (void **) tagger = (void *)-2;
if (*ierr) return;
PETSC_FORTRAN_OBJECT_C_NULL_TO_F_DESTROYED(tagger);
 }
PETSC_EXTERN void  vectaggersetup_(VecTagger tagger, int *ierr)
{
CHKFORTRANNULLOBJECT(tagger);
*ierr = VecTaggerSetUp(
	(VecTagger)PetscToPointer((tagger) ));
}
PETSC_EXTERN void  vectaggersetblocksize_(VecTagger tagger,PetscInt *blocksize, int *ierr)
{
CHKFORTRANNULLOBJECT(tagger);
*ierr = VecTaggerSetBlockSize(
	(VecTagger)PetscToPointer((tagger) ),*blocksize);
}
PETSC_EXTERN void  vectaggergetblocksize_(VecTagger tagger,PetscInt *blocksize, int *ierr)
{
CHKFORTRANNULLOBJECT(tagger);
CHKFORTRANNULLINTEGER(blocksize);
*ierr = VecTaggerGetBlockSize(
	(VecTagger)PetscToPointer((tagger) ),blocksize);
}
PETSC_EXTERN void  vectaggersetinvert_(VecTagger tagger,PetscBool *invert, int *ierr)
{
CHKFORTRANNULLOBJECT(tagger);
*ierr = VecTaggerSetInvert(
	(VecTagger)PetscToPointer((tagger) ),*invert);
}
PETSC_EXTERN void  vectaggergetinvert_(VecTagger tagger,PetscBool *invert, int *ierr)
{
CHKFORTRANNULLOBJECT(tagger);
*ierr = VecTaggerGetInvert(
	(VecTagger)PetscToPointer((tagger) ),invert);
}
PETSC_EXTERN void  vectaggerview_(VecTagger tagger,PetscViewer viewer, int *ierr)
{
CHKFORTRANNULLOBJECT(tagger);
CHKFORTRANNULLOBJECT(viewer);
*ierr = VecTaggerView(
	(VecTagger)PetscToPointer((tagger) ),PetscPatchDefaultViewers((PetscViewer*)viewer));
}
#if defined(__cplusplus)
}
#endif
