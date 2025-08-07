#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* pf.c */
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

#include "petscpf.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pfapplyvec_ PFAPPLYVEC
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pfapplyvec_ pfapplyvec
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pfapply_ PFAPPLY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pfapply_ pfapply
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pfviewfromoptions_ PFVIEWFROMOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pfviewfromoptions_ pfviewfromoptions
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pfview_ PFVIEW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pfview_ pfview
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pfgettype_ PFGETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pfgettype_ pfgettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pfsettype_ PFSETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pfsettype_ pfsettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pfsetfromoptions_ PFSETFROMOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pfsetfromoptions_ pfsetfromoptions
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  pfapplyvec_(PF pf,Vec x,Vec y, int *ierr)
{
CHKFORTRANNULLOBJECT(pf);
CHKFORTRANNULLOBJECT(x);
CHKFORTRANNULLOBJECT(y);
*ierr = PFApplyVec(
	(PF)PetscToPointer((pf) ),
	(Vec)PetscToPointer((x) ),
	(Vec)PetscToPointer((y) ));
}
PETSC_EXTERN void  pfapply_(PF pf,PetscInt *n, PetscScalar *x,PetscScalar *y, int *ierr)
{
CHKFORTRANNULLOBJECT(pf);
CHKFORTRANNULLSCALAR(x);
CHKFORTRANNULLSCALAR(y);
*ierr = PFApply(
	(PF)PetscToPointer((pf) ),*n,x,y);
}
PETSC_EXTERN void  pfviewfromoptions_(PF A,PetscObject obj, char name[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(A);
CHKFORTRANNULLOBJECT(obj);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = PFViewFromOptions(
	(PF)PetscToPointer((A) ),
	(PetscObject)PetscToPointer((obj) ),_cltmp0);
  FREECHAR(name,_cltmp0);
}
PETSC_EXTERN void  pfview_(PF pf,PetscViewer viewer, int *ierr)
{
CHKFORTRANNULLOBJECT(pf);
CHKFORTRANNULLOBJECT(viewer);
*ierr = PFView(
	(PF)PetscToPointer((pf) ),PetscPatchDefaultViewers((PetscViewer*)viewer));
}
PETSC_EXTERN void  pfgettype_(PF pf,char *type, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(pf);
*ierr = PFGetType(
	(PF)PetscToPointer((pf) ),(const char **)&_cltmp0);
/* insert C-to-Fortran conversion for type */
*ierr = PetscStrncpy(type, _cltmp0, cl0);
                        if (*ierr) return;
                        FIXRETURNCHAR(PETSC_TRUE, type, cl0);
}
PETSC_EXTERN void  pfsettype_(PF pf,char *type,void*ctx, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(pf);
/* insert Fortran-to-C conversion for type */
  FIXCHAR(type,cl0,_cltmp0);
*ierr = PFSetType(
	(PF)PetscToPointer((pf) ),_cltmp0,ctx);
  FREECHAR(type,_cltmp0);
}
PETSC_EXTERN void  pfsetfromoptions_(PF pf, int *ierr)
{
CHKFORTRANNULLOBJECT(pf);
*ierr = PFSetFromOptions(
	(PF)PetscToPointer((pf) ));
}
#if defined(__cplusplus)
}
#endif
