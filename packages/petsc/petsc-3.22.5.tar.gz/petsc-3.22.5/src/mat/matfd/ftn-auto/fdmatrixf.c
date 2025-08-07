#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* fdmatrix.c */
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

#include "petscmat.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matfdcoloringview_ MATFDCOLORINGVIEW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matfdcoloringview_ matfdcoloringview
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matfdcoloringsetparameters_ MATFDCOLORINGSETPARAMETERS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matfdcoloringsetparameters_ matfdcoloringsetparameters
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matfdcoloringsetblocksize_ MATFDCOLORINGSETBLOCKSIZE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matfdcoloringsetblocksize_ matfdcoloringsetblocksize
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matfdcoloringsetup_ MATFDCOLORINGSETUP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matfdcoloringsetup_ matfdcoloringsetup
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matfdcoloringsetfromoptions_ MATFDCOLORINGSETFROMOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matfdcoloringsetfromoptions_ matfdcoloringsetfromoptions
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matfdcoloringsettype_ MATFDCOLORINGSETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matfdcoloringsettype_ matfdcoloringsettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matfdcoloringcreate_ MATFDCOLORINGCREATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matfdcoloringcreate_ matfdcoloringcreate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matfdcoloringdestroy_ MATFDCOLORINGDESTROY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matfdcoloringdestroy_ matfdcoloringdestroy
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matfdcoloringapply_ MATFDCOLORINGAPPLY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matfdcoloringapply_ matfdcoloringapply
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  matfdcoloringview_(MatFDColoring c,PetscViewer viewer, int *ierr)
{
CHKFORTRANNULLOBJECT(c);
CHKFORTRANNULLOBJECT(viewer);
*ierr = MatFDColoringView(
	(MatFDColoring)PetscToPointer((c) ),PetscPatchDefaultViewers((PetscViewer*)viewer));
}
PETSC_EXTERN void  matfdcoloringsetparameters_(MatFDColoring matfd,PetscReal *error,PetscReal *umin, int *ierr)
{
CHKFORTRANNULLOBJECT(matfd);
*ierr = MatFDColoringSetParameters(
	(MatFDColoring)PetscToPointer((matfd) ),*error,*umin);
}
PETSC_EXTERN void  matfdcoloringsetblocksize_(MatFDColoring matfd,PetscInt *brows,PetscInt *bcols, int *ierr)
{
CHKFORTRANNULLOBJECT(matfd);
*ierr = MatFDColoringSetBlockSize(
	(MatFDColoring)PetscToPointer((matfd) ),*brows,*bcols);
}
PETSC_EXTERN void  matfdcoloringsetup_(Mat mat,ISColoring iscoloring,MatFDColoring color, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLOBJECT(iscoloring);
CHKFORTRANNULLOBJECT(color);
*ierr = MatFDColoringSetUp(
	(Mat)PetscToPointer((mat) ),
	(ISColoring)PetscToPointer((iscoloring) ),
	(MatFDColoring)PetscToPointer((color) ));
}
PETSC_EXTERN void  matfdcoloringsetfromoptions_(MatFDColoring matfd, int *ierr)
{
CHKFORTRANNULLOBJECT(matfd);
*ierr = MatFDColoringSetFromOptions(
	(MatFDColoring)PetscToPointer((matfd) ));
}
PETSC_EXTERN void  matfdcoloringsettype_(MatFDColoring matfd,char *type, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(matfd);
/* insert Fortran-to-C conversion for type */
  FIXCHAR(type,cl0,_cltmp0);
*ierr = MatFDColoringSetType(
	(MatFDColoring)PetscToPointer((matfd) ),_cltmp0);
  FREECHAR(type,_cltmp0);
}
PETSC_EXTERN void  matfdcoloringcreate_(Mat mat,ISColoring iscoloring,MatFDColoring *color, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLOBJECT(iscoloring);
PetscBool color_null = !*(void**) color ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(color);
*ierr = MatFDColoringCreate(
	(Mat)PetscToPointer((mat) ),
	(ISColoring)PetscToPointer((iscoloring) ),color);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! color_null && !*(void**) color) * (void **) color = (void *)-2;
}
PETSC_EXTERN void  matfdcoloringdestroy_(MatFDColoring *c, int *ierr)
{
PETSC_FORTRAN_OBJECT_F_DESTROYED_TO_C_NULL(c);
 PetscBool c_null = !*(void**) c ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(c);
*ierr = MatFDColoringDestroy(c);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! c_null && !*(void**) c) * (void **) c = (void *)-2;
if (*ierr) return;
PETSC_FORTRAN_OBJECT_C_NULL_TO_F_DESTROYED(c);
 }
PETSC_EXTERN void  matfdcoloringapply_(Mat J,MatFDColoring coloring,Vec x1,void*sctx, int *ierr)
{
CHKFORTRANNULLOBJECT(J);
CHKFORTRANNULLOBJECT(coloring);
CHKFORTRANNULLOBJECT(x1);
*ierr = MatFDColoringApply(
	(Mat)PetscToPointer((J) ),
	(MatFDColoring)PetscToPointer((coloring) ),
	(Vec)PetscToPointer((x1) ),sctx);
}
#if defined(__cplusplus)
}
#endif
